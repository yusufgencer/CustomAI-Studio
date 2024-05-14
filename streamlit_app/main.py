import streamlit as st
import base64
import os
from typing import Generator
from groq import Groq
from typing import Optional, Dict, Union

class CustomAIStudio:
    """
    CustomAIStudio is a Streamlit-based application for creating and managing AI assistants.

    Attributes:
        prompts_directory (str): Path to the directory containing prompt files.
        svg_icon_path (str): Path to the SVG icon file for the page configuration.
        sidebar_image_path (str): Path to the image file displayed in the sidebar.
        groq_api_key (Optional[str]): API key for accessing the Groq service.
        client (Optional[Groq]): Groq client initialized with the API key.
        models (Dict[str, Dict[str, Optional[Union[str, int]]]]): Dictionary containing information about different AI models.
    """

    def __init__(self):
        """
        Initializes the CustomAIStudio class with default paths and model configurations.
        """
        self.prompts_directory: str = "streamlit_app/prompt_lib"
        self.svg_icon_path: str = 'streamlit_app/page_config_logo.svg'
        self.sidebar_image_path: str = "streamlit_app/sidebar_logo.png"
        self.groq_api_key: Optional[str] = None
        self.client: Optional[Groq] = None
        self.models: Dict[str, Dict[str, Optional[Union[str, int]]]] = {
            "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
            "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
            "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
            "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
        }


    def get_svg_base64(self, file_path: str) -> str:
        """
        Reads an SVG file, encodes its contents to base64, and returns a data URI.

        Args:
            file_path (str): The path to the SVG file.

        Returns:
            str: The base64-encoded data URI of the SVG file.
        """
        with open(file_path, 'rb') as svg_file:
            encoded = base64.b64encode(svg_file.read()).decode('utf-8')
        return f"data:image/svg+xml;base64,{encoded}"

    def read_prompts_from_directory(self, directory: str) -> Dict[str, str]:
        """
        Reads all text files in a directory and returns their contents as prompts.

        Args:
            directory (str): The path to the directory containing prompt files.

        Returns:
            Dict[str, str]: A dictionary where the keys are role names derived from filenames
                            and the values are the contents of the corresponding files.
        """
        prompts = {}
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                role_name = filename.replace("_prompt.txt", "").replace("_", " ").title()
                with open(os.path.join(directory, filename), "r") as file:
                    prompt_content = file.read()
                    prompts[role_name] = prompt_content
        return prompts

    def set_page_config(self) -> None:
        """
        Sets the Streamlit page configuration, including the page icon, layout, title, 
        initial sidebar state, and menu items.

        The page icon is set using the base64-encoded SVG image obtained from the 
        get_svg_base64 method.

        Returns:
            None
        """
        svg_icon = self.get_svg_base64(self.svg_icon_path)
        st.set_page_config(
            page_icon=svg_icon, 
            layout="wide", 
            page_title="CustomAI Studio",
            initial_sidebar_state="expanded",
            menu_items={
                'About': "This app was developed by Yusuf Gençer. If you have any questions or feedback, feel free to reach out on [LinkedIn](https://www.linkedin.com/in/yusufgencer/)."
            }
        )

    def display_sidebar(self) -> None:
        """
        Displays the sidebar in the Streamlit application.

        This includes displaying an image, an input field for the Groq API key,
        buttons for navigating between pages, and setting the default page if none is selected.

        Returns:
            None
        """
        st.sidebar.image(self.sidebar_image_path, use_column_width=True)

        self.groq_api_key = st.sidebar.text_input(
            "Enter Groq API Key:", 
            type="password", 
            help=(
                "Tip: To keep your API key saved, avoid refreshing the page.\n\n"
                "How to generate an API key:\n"
                "1. Go to the Groq Console: https://console.groq.com/keys\n"
                "2. Follow the instructions to create a new API key.\n"
                "3. Copy and paste the key here."
            )
        )

        if self.groq_api_key:
            st.session_state["GROQ_API_KEY"] = self.groq_api_key
            st.sidebar.write("API Key stored successfully!")

        # Add navigation buttons for Chat Page and Create Assistant Page
        col1, col2 = st.sidebar.columns([1, 1])
        if col1.button("Chat Page"):
            st.session_state.page = "Chat Page"
        if col2.button("Create Assistant"):
            st.session_state.page = "Create Assistant"

        # Set default page if none is selected
        if "page" not in st.session_state:
            st.session_state.page = "Chat Page"

    def setup_prompts(self) -> None:
        """
        Sets up the prompts by reading them from the specified directory and initializing
        the session state with default and custom assistant prompts.

        If the "assistants" key is not present in the session state, it creates it with
        a default assistant prompt and any additional prompts read from the directory.

        Returns:
            None
        """
        prompts: Dict[str, str] = self.read_prompts_from_directory(self.prompts_directory)
        
        if "assistants" not in st.session_state:
            st.session_state.assistants = {
                "Default": (
                    "Hello! I'm your helpful assistant, ready to assist you with any questions or tasks you have. "
                    "Whether you need information, advice, or just someone to chat with, I'm here to help. "
                    "Just let me know how I can assist you today!"
                ),
                **prompts
            }

    def sidebar_assistant_management(self) -> None:
        """
        Manages the assistant selection and deletion functionality in the sidebar.

        This method allows the user to select an assistant from a dropdown menu and delete the selected assistant.
        The selected assistant is stored in the session state.

        Returns:
            None
        """
        selected_assistant: str = st.sidebar.selectbox(
            "Select an Assistant:",
            options=list(st.session_state.assistants.keys())
        )
        
        st.session_state['selected_assistant'] = selected_assistant

        if st.sidebar.button("Delete Selected Assistant"):
            if selected_assistant in st.session_state.assistants:
                del st.session_state.assistants[selected_assistant]
                st.sidebar.write(f"Assistant '{selected_assistant}' deleted successfully!")
            else:
                st.sidebar.write("No assistant selected or assistant not found!")

    def generate_chat_responses(self, chat_completion) -> Generator[str, None, None]:
        """
        Yields chat response content from the Groq API response.

        Args:
            chat_completion: The response from the Groq API, expected to be an iterable
                             containing chunks of data with chat response content.

        Yields:
            str: The content of each chunk in the chat completion response.
        """
        for chunk in chat_completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def handle_api_key(self) -> None:
        """
        Handles the API key retrieval and storage in the session state.

        This method checks if the Groq API key is present in the session state or secrets.
        If not found, it displays an error and stops the execution. If found, it initializes the Groq client.

        Returns:
            None
        """
        if "GROQ_API_KEY" not in st.session_state or st.session_state["GROQ_API_KEY"] is None:
            if "GROQ_API_KEY" in st.secrets:
                st.session_state["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
            else:
                st.error("API Key is required to proceed.")
                st.stop()

        self.client = Groq(api_key=st.session_state["GROQ_API_KEY"])

    def render_chat_page(self):
        st.title("CustomAI Studio Powered by Groq")
        if 'selected_assistant' in st.session_state:
            st.write(f"Selected assistant: {st.session_state['selected_assistant']}")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "selected_model" not in st.session_state:
            st.session_state.selected_model = None

        col1, col2 = st.columns(2)

        with col1:
            model_option = st.selectbox(
                "Choose a model:",
                options=list(self.models.keys()),
                format_func=lambda x: self.models[x]["name"],
                index=1
            )

        if st.session_state.selected_model != model_option:
            st.session_state.selected_model = model_option

        max_tokens_range = self.models[model_option]["tokens"]

        with col2:
            max_tokens = st.slider(
                "Max Tokens:",
                min_value=248,
                max_value=max_tokens_range,
                value=min(32768, max_tokens_range),
                step=248,
                help=f"Set the maximum length for the model's response. This limits the number of words generated. The maximum limit for the selected model is {max_tokens_range} tokens."
            )

        def clear_chat():
            st.session_state.messages = []

        for message in st.session_state.messages:
            if message["role"] != "system":
                avatar = '✨' if message["role"] == "assistant" else '👨‍💻'
                with st.chat_message(message["role"], avatar=avatar):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Enter your prompt here..."):
            st.session_state.messages.append({
                "role": "system",
                "content": st.session_state.assistants.get(st.session_state['selected_assistant'], "Invalid assistant"),
            })
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.chat_message("user", avatar='👨‍💻'):
                st.markdown(prompt)

            full_response = None

            try:
                chat_completion = self.client.chat.completions.create(
                    model=model_option,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    max_tokens=max_tokens,
                    stream=True
                )

                with st.chat_message("assistant", avatar="✨"):
                    chat_responses_generator = self.generate_chat_responses(chat_completion)
                    full_response = st.write_stream(chat_responses_generator)
            except Exception as e:
                error_message = str(e)
                if 'rate_limit_exceeded' in error_message:
                    st.error("Rate limit exceeded. Please try again in a few moments.", icon="🚨")
                    st.info("To avoid this issue in the future, consider using your own API key to manage rate limits independently.")
                else:
                    st.error(error_message, icon="🚨")

            if full_response is not None:
                if isinstance(full_response, str):
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    combined_response = "\n".join(str(item) for item in full_response)
                    st.session_state.messages.append({"role": "assistant", "content": combined_response})
            else:
                st.warning("No response was generated.", icon="⚠️")

        if st.button("Clear Chat", key="clear_chat"):
            clear_chat()
            st.rerun()

    def render_create_assistant_page(self) -> None:
        """
        Renders the create assistant page in the Streamlit app.

        Returns
        -------
        None
        """
        st.title("Create Your CustomAI Assistant")
        assistant_name = st.text_input("Assistant Name:")
        prompt_option = st.selectbox("Choose Prompt Option:", ["Custom Prompt", "Auto-generate Prompt"])

        if prompt_option == "Custom Prompt":
            st.session_state.user_prompt = st.text_area("Enter your custom prompt:")
        elif prompt_option == "Auto-generate Prompt":
            user_input = st.text_area("Provide input for auto-prompt generation:")
            if st.button("Generate Prompt", key="generate_prompt"):
                try:
                    generated_prompt = self._generate_prompt(user_input)
                    st.session_state.generated_prompt = generated_prompt
                    st.success("Prompt generated succesfully")
                    st.info(f"{generated_prompt}")
                except Exception as e:
                    st.error(f"Failed to generate prompt: {e}")

        if st.button("Create Assistant", key="create_assistant_final"):
            if prompt_option == "Custom Prompt":
                final_prompt = st.session_state.user_prompt
            elif prompt_option == "Auto-generate Prompt":
                final_prompt = st.session_state.generated_prompt
            if assistant_name:
                self._create_assistant(assistant_name, final_prompt)
                st.success(f"Assistant '{assistant_name}' created successfully with prompt:")
                st.info(f"{final_prompt}")
            else:
                st.write("Please enter a valid assistant name.")

    def _get_system_prompt(self) -> str:
        """
        Reads the system prompt from a file.

        Returns
        -------
        str
            The system prompt.
        """
        with open("streamlit_app/system_prompt.txt", "r", encoding="utf-8") as file:
            return file.read()

    def _generate_prompt(self, user_input: str) -> str:
        """
        Generates a prompt based on the user input.

        Parameters
        ----------
        user_input : str
            The user input for auto-prompt generation.

        Returns
        -------
        str
            The generated prompt.
        """
        system_prompt = self._get_system_prompt()
        model_option = "llama3-70b-8192"
        max_tokens = 8192
        chat_completion = self.client.chat.completions.create(
            model=model_option,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            max_tokens=max_tokens,
            stream=True
        )
        generated_prompt = ""
        for response in self.generate_chat_responses(chat_completion):
            generated_prompt += response
        return generated_prompt

    def _create_assistant(self, assistant_name: str, prompt: str) -> None:
        """
        Creates a custom AI assistant with the given name and prompt.

        Parameters
        ----------
        assistant_name : str
            The name of the assistant.
        prompt : str
            The prompt for the assistant.

        Returns
        -------
        None
        """
        st.session_state.assistants[assistant_name] = prompt

    def run(self):
        self.set_page_config()
        self.display_sidebar()
        self.setup_prompts()
        self.sidebar_assistant_management()
        self.handle_api_key()

        if st.session_state.page == "Chat Page":
            self.render_chat_page()
        elif st.session_state.page == "Create Assistant":
            self.render_create_assistant_page()

if __name__ == "__main__":
    app = CustomAIStudio()
    app.run()
