from mcp.server.fastmcp import FastMCP
import os 
from openai import OpenAI

# Initialize FastMCP server
mcp = FastMCP("writer")
MODEL = 'qwen2.5-coder-7b-instruct'
#llm_client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key='lmstudio')
llm_client = OpenAI(base_url="http://10.137.58.215:1234/v1", api_key='lmstudio')

@mcp.tool()
def write_file(name: str, content: str, dir: str) -> str:
    """Function to create files in the file system using a name, content and the directory path
    Args:
        name: the name of the file that will be created
        content: the content of the file that will be grated
        dir: the raw path to the specific folder where the file shall be saved
    Returns:
        str: confirmation message of the successfully created file"""
    
    base_dir = os.path.dirname(__file__)
    abs_dir = os.path.abspath(os.path.join(base_dir, dir)) if dir else os.getcwd()
    os.makedirs(abs_dir, exist_ok=True)
    file_path = os.path.join(abs_dir, name)
    print(f'recibi name={name} y directorio = {dir} y al final el filepath es = {file_path}')
    try:
        with open(file_path, 'w', encoding='utf-8') as doc:
            doc.write(content)
        return f"Archivo {name} creado"
    except Exception as e:
        return f"Error creando el archivo {name} : {str(e)}"
    
@mcp.tool()
def read_file(path:str) -> str:
    """Function to read files from the file system using a directory path
    Args:
        path: the raw path to the specific folder where the file to be read is located
    Returns:
        str: with the content of the file read.
    """
    base_dir = os.path.dirname(__file__)
    abs_dir = os.path.abspath(os.path.join(base_dir, path))
    try:
        with open(abs_dir, 'r', encoding='utf-8') as doc:
            content = doc.read()
        return content
    except FileNotFoundError:
        return f"El archivo {path} no se encontro"
    except Exception as e:
        return f"Ocurrio un error {str(e)}"
    
@mcp.tool()
def create_script(req_path: str, output_name: str, output_dir: str) -> str:
    """Function to create a pythons script based on a requirements file given by the user and save the script in a desired path
    Args:
        req_path: the path where the requirements file is located
        output_name: the name of the script generated 
        output_dir: the desired path where the script will be saved
    Returns:
        str: confirmation message of the successfully created file"""
    
    requirements= read_file(req_path)
    if requirements.startswith("El archivo") or requirements.startswith("Ocurrio un error"):
        return requirements
    #create code, make a call to the LLM to creathe the script
    prompt = f'based on the software requirements listed in {requirements} please generate a python script ready to execute to implement this requirements, make sure the script works fine and the output database is named as database.json'
    try:
        result = llm_client.chat.completions.create(
            model= MODEL,
            messages= [{'role': 'user', 'content': prompt}],
            max_tokens= 1500,
            temperature=0.7
        )
        generated_script = result.choices[0].message.content
    except Exception as e:
        return f'Error generating code {str(e)}' 
    
    result = write_file(output_name, generated_script, output_dir)
    return f'script generated: {result}'

@mcp.tool()
def create_test_case(req_path: str, output_name: str, output_dir: str):
    """Function to create a Test cases file based on a requirements file given by the user and save the file in a desired path
    Args:
        req_path: the path where the requirements file is located
        output_name: the name of the test cases file generated 
        output_dir: the desired path where the test cases file will be saved
    Returns:
        str: confirmation message of the successfully created file"""
    requirements= read_file(req_path)
    if requirements.startswith("El archivo") or requirements.startswith("Ocurrio un error"):
        return requirements
    #create code, make a call to the LLM to creathe the script
    prompt = f'based on the software requirements listed in {requirements} please generate file with a list of test cases pseudocode to cover all the possible scenarios'
    try:
        result = llm_client.chat.completions.create(
            model= MODEL,
            messages= [{'role': 'user', 'content': prompt}],
            max_tokens= 1500
        )
        generated_script = result.choices[0].message.content
        
    except Exception as e:
        return f'Error generating code {str(e)}' 
    
    result = write_file(output_name, generated_script, output_dir)
    return f'Test cases generated: {result}'

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

