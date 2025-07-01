import flet as ft
import requests


# The URL endpoint to send the POST request to
url = "http://127.0.0.1:5000/receive_data"

# Data to be sent in the request body (as form-encoded data)
payload_json = {
    "filter": "",
    "timer": "5"
}


def main(page: ft.Page):
    prompt_text = []
    mix_timer = 5  # default value



    def on_text_change(e):
        nonlocal prompt_text
        # Split input text into words and store in prompt_text
        prompt_text = [word for word in e.control.value.strip().split() if word]
        # Optionally, update a label or print for debugging
        print("prompt_text:", prompt_text)
    
    def add_clicked(e):
        prompt_text = ""

        #send values

        text_filterinput.value = ""  # Clear the input field
        # Optionally, update a label or print for debugging
        print("Add button clicked, prompt_text cleared.") 

        page.update()





    def on_slider_change(e):
        nonlocal mix_timer
        mix_timer = int(e.control.value)
        # Optionally, update a label or print for debugging
        print("mix_timer:", mix_timer)


    def send_values(e):
        # This function can be used to send the values to a server or process them
        print("Sending values:")
        print("prompt_text:", prompt_text)
        print("mix_timer:", mix_timer)

        try:
            # Update the payload with the current values
            payload_json["filter"] = " ".join(prompt_text)  # Join words with spaces
            payload_json["timer"] = str(mix_timer)  # Convert timer to string
            response_json = requests.post(url, json=payload_json)
            response_json.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            print("POST request with JSON data successful!")
            print("Response JSON:", response_json.json())
        except requests.RequestException as e:
            print("An error occurred while sending the request:", e)


    text_Title = ft.Text(
        "MixSpace / MixStudio",
        size=20,
        weight="bold",
        text_align="center",
    )

    text_filterinput = ft.TextField(
        label="Add filters",
        on_change=on_text_change,
        width=300,
        expand=True,
    )

    slider_timer = ft.Slider(
        min=5,
        max=20,
        divisions=15,
        value=5,
        label="{value}",
        on_change=on_slider_change,
        width=300,
    )

    view_title = ft.Column(
        width=300,
        controls=[
            text_Title,
        ]
    ) 

    view_filters = ft.Column(
        width=300,
        controls=[
            ft.Row(
                controls=[
                    text_filterinput,
                    # ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=add_clicked),
                ]
            ),
            
        ]
    ) 

    view_timer = ft.Column(
        width=300,
        controls=[
            ft.Text("Shuffle Timer:"),
            slider_timer,
        ]
    )

    page.add(
        ft.Column([
            # text_Title,
            view_title,
            view_filters,
            view_timer,
            ft.ElevatedButton(
                text="Send Values",
                on_click=send_values,
                width=300,
                expand=True,
            ),
            
        ])
    )


    page.title = "MixSpace / MixStudio"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 200

ft.app(target=main)