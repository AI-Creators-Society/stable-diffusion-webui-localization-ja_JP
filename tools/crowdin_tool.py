import os
import json
from tqdm import tqdm
from crowdin_api import CrowdinClient

# setup variables
project_token = os.environ['crowdin_api_token']
project_id = 552413
stablediffusion_dir_id = 61
extension_dir_id = 65

# fetch all crowdin source files
client = CrowdinClient(token=project_token)
stablediffusion_files = client.source_files.with_fetch_all(
).list_files(projectId=project_id, directoryId=stablediffusion_dir_id)
extension_files = client.source_files.with_fetch_all(
).list_files(projectId=project_id, directoryId=extension_dir_id)

# function to get file progress and print to markdown strings


def crowndin(file_scope):
    progress_list = []

    # init progress bar
    file_count = len(file_scope['data'])
    progress = tqdm(desc='requesting: ', total=file_count)

    for filedata in file_scope['data']:
        # setting variables
        file_id = filedata['data']['id']
        file_name = filedata['data']['name'].replace('.json', '')
        file_path = filedata['data']['path'].replace('/main/', './')
        file_progress = client.translation_status.get_file_progress(
            projectId=project_id, fileId=file_id)['data'][0]['data']['translationProgress']
        check_box = '[ ]'
        if file_progress == 100:
            check_box = '[x]'

        # Get extension url
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # find key contains '.git' convert to url
                for key in data.keys():
                    if '.git' in key:
                        extension_url = key.replace('.git', '')
                    elif file_name == 'StableDiffusion':
                        extension_url = 'https://github.com/AUTOMATIC1111/stable-diffusion-webui'
                    elif file_name == 'ExtensionList':
                        extension_url = 'https://raw.githubusercontent.com/wiki/AUTOMATIC1111/stable-diffusion-webui/Extensions-index.md'
                    else:
                        extension_url = ''
        else:
            print(f"url not found at '{file_path}'")

        progress_list.append(
            f"- {check_box} ![{file_name} translated {file_progress}%](https://geps.dev/progress/{file_progress}?dangerColor=c9f2dc&warningColor=6cc570&successColor=00ff7f) [{file_name}]({extension_url})")

        progress.update(1)

    return progress_list


# read README.md
with open('./README.md', 'r', encoding='utf-8') as file:
    readme_content = file.read()

# extract contents without progress section
start_index = readme_content.find('## ローカライズの進捗')
end_index = readme_content.find('# Getting Started')
top_content = readme_content[0:start_index]
bottom_content = readme_content[end_index:len(readme_content)]

# generating new progress content
middle_content = '## ローカライズの進捗\n\n<details>\n<summary>WebUI</summary>\n\n'
for string in crowndin(stablediffusion_files):
    middle_content += f"{string}\n"
middle_content += '</details>\n\n<details>\n<summary>拡張機能</summary>\n\n'
for string in crowndin(extension_files):
    middle_content += f"{string}\n"
middle_content += '</details>\n\n'

# write new contents back to README.md
new_content = top_content+middle_content+bottom_content
with open('./README.md', 'w', encoding='utf-8') as f:
    f.write(new_content)
