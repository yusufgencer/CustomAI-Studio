
# CustomAI Studio

CustomAI Studio is a Streamlit-based application for creating and managing AI assistants. This application allows users to input custom prompts or auto-generate prompts for new assistants, interact with the assistants through a chat interface, and manage multiple assistants.

## Features

- **Create Assistants**: Input custom prompts or auto-generate prompts for new assistants.
- **Chat Interface**: Interact with assistants using a chat interface.
- **Assistant Management**: Select, create, and delete assistants easily.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yusufgencer/CustomAI-Studio.git
    cd customai-studio
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

Run the Streamlit application:
```sh
streamlit run streamlit_app/main.py
```

## How It Works

### 1. Page Configuration

The application sets up the page configuration with a custom SVG icon, wide layout, and a friendly "About" message.

### 2. Sidebar

The sidebar includes:
- An image at the top.
- Input for the Groq API key.
- Buttons to navigate between the "Chat Page" and "Create Assistant" page.
- Assistant selection and management options.

### 3. Prompts

Prompts are read from a specified directory and initialized in the session state. The application includes a default assistant prompt and any additional prompts read from the directory.

### 4. Chat Page

On the "Chat Page", users can:
- Select a model.
- Input prompts.
- View chat responses from the assistant.
- Clear chat history.

### 5. Create Assistant Page

On the "Create Assistant" page, users can:
- Enter an assistant name.
- Choose between inputting a custom prompt or auto-generating a prompt.
- Create a new assistant with the specified prompt.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

Developed by Yusuf Gencer. Feel free to reach out on [LinkedIn](https://www.linkedin.com/in/yusufgencer/) for any questions or feedback.
