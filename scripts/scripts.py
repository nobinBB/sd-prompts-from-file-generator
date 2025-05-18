import modules.scripts as scripts
import gradio as gr
from modules import script_callbacks
import tempfile

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False, title="Prompts from File Generator") as ui_component:
        max_forms = 10
        form_count = gr.Number(label="フォーム数（1-10まで）", value=1, minimum=1, maximum=max_forms, step=1)
        prompts = [gr.Textbox(label=f"プロンプト [{i+1}]", visible=(i == 0)) for i in range(max_forms)]
        nums = [gr.Number(label=f"生成枚数 [{i+1}]", value=10, minimum=1, maximum=10000, step=1, visible=(i == 0)) for i in range(max_forms)]

        status_text = gr.Textbox(label="ステータス", interactive=False)
        generate_button = gr.Button("生成する")
        generated_text = gr.Textbox(label="生成されたテキスト-表示されている部分をクリックし、Ctrl+Aで全てを選択し、Ctrl+Cでコピー", interactive=False, lines=10, elem_id="generated_text")
        download_file = gr.File(label="テキストをダウンロード", interactive=False)

        def update_visibility(count):
            return [gr.update(visible=(i < int(count))) for i in range(max_forms)] * 2

        form_count.change(
            fn=update_visibility,
            inputs=[form_count],
            outputs=prompts + nums
        )

        def generate_text(*all_inputs):
            count = int(all_inputs[0])  # フォーム数
            lines = []
            error = None
            for i in range(count):
                prompt = all_inputs[1 + i]
                num_images = all_inputs[1 + max_forms + i]
                # どちらかでも空欄ならエラーにする
                if not prompt or not str(prompt).strip():
                    error = f"{i+1}番目のプロンプトが空です"
                    break
                if not num_images or int(num_images) <= 0:
                    error = f"{i+1}番目の生成枚数が未入力または0以下です"
                    break
                prompt_text = prompt.replace("\n", ", ")
                for _ in range(int(num_images)):
                    lines.append(f'--prompt "{prompt_text}"')
            if error:
                return "", error, None
            if not lines:
                return "", "すべてのフィールドに入力してください", None
            output = "\n".join(lines)
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                f.write(output)
                temp_file_path = f.name
            return output, "生成完了", temp_file_path


        generate_button.click(
            fn=generate_text,
            inputs=[form_count] + prompts + nums,
            outputs=[generated_text, status_text, download_file]
        )


        return [(ui_component, "Prompts from File Generator", "prompts_generator_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
