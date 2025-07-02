import flet as ft
import requests
import json

# from flet.border import BorderSide
# from flet.buttons import RoundedRectangleBorder


# The URL endpoint to send the POST request to
url = "https://936a-66-253-203-14.ngrok-free.app"

# Data to be sent in the request body (as form-encoded data)
# payload_json = {
#     "filter": "",
#     "timer": "5"
# }

payload_json = {
    'type': 'settings',
    'payload': {
        'filter': "",
        'timer': "5"
    }
}


height_width = 500  # Default size for the window and controls

def main(page: ft.Page):
    page.always_on_top = True  # Keep the window always on top
    page.window.width = height_width
    page.window.height = 450
    page.window.resizable = False
    page.window.maximizable = False
    page.title_bar_hidden = True  # Hide the title bar
    page.window.center()  # Center the window on the screen
    
    #chanmge background color to black
    page.bgcolor = ft.Colors.BLACK

    page.theme = ft.Theme(
        slider_theme=ft.SliderTheme(

            value_indicator_text_style=ft.TextStyle(
                color=ft.Colors.WHITE,  # Set the text color of the value indicator
            )
        )
    )



    page.update()


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

    def no_action(e):
        # This function does nothing, can be used for testing purposes
        print("No action performed.")

    def send_values(e):
        # This function can be used to send the values to a server or process them
        print("Sending values:")
        print("prompt_text:", prompt_text)
        print("mix_timer:", mix_timer)

        try:
            # Update the payload with the current values
            payload_json["payload"]["filter"] = " ".join(prompt_text)  # Join words with spaces
            payload_json["payload"]["timer"] = str(mix_timer)  # Convert timer to string
            # Send the POST request with JSON data
            # response_json = requests.post(url, json=payload_json)
            json_object_string = json.dumps(payload_json, indent=4)
            print("Payload JSON:", payload_json)  # Print the payload for debugging
            print("Payload JSON String:", json_object_string)  # Print the JSON string for debugging


            response_json = requests.post(url, data=json_object_string)
            response_json.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
            print("POST request with form data successful!")
            print("Response JSON:", response_json.json())
        except requests.RequestException as e:
            print(f"An error occurred with form data: {e}")


    text_Title = ft.Text(
        "MixSpace",
        size=20,
        weight="bold",
        text_align="center",
    )

    img_slider = ft.Image(
        src=f"Images/Sliders.png",
        width=100,
        height=100,
        fit=ft.ImageFit.CONTAIN,
    )
    


    text_filterinput = ft.TextField(
        label="Add filters",
        on_change=on_text_change,
        width=height_width,
        expand=True,
    )

    slider_timer = ft.Slider(
            min=5,
            max=20,
            divisions=15,
            value=5,
            label="{value}",
            on_change=on_slider_change,
            
            
            thumb_color=ft.Colors.GREEN,
            active_color=ft.Colors.GREEN_900,
            inactive_color=ft.Colors.GREEN_200,
            
            width=height_width, 
    )



    view_title = ft.Column(
        width=height_width,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            text_Title,
        ]
    ) 

    view_filters = ft.Column(
        width=height_width,
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
        width=height_width,
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
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                # horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                width=height_width,
                controls=[
                    ft.ElevatedButton(
                        content=ft.Image("MysticalMagical/llm-music/src/Images/Sliders_raw.png"),
                        text="Send Values",
                        on_click=no_action,
                        width=150,
                        expand=True,
                        # style=ft.ButtonStyle(
                        #     side={
                        #         ft.ControlState.HOVERED: ft.BorderSide(0, ft.Colors.GREEN_900), # 2 pixels wide, green color
                        #     }
                        # ),
                        bgcolor=ft.Colors.TRANSPARENT,

                    ),
                    # insert image here 
                    img_slider,
                    
                    ft.ElevatedButton(
                        content=ft.Image("Images/music_disc.gif"),
                        text="Send Values",
                        on_click=send_values,
                        width=150,
                        expand=True,
                        bgcolor=ft.Colors.TRANSPARENT,
                    ),
                ]
            ),

            
            
            
        ])
    )


    page.title = "MixSpace"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.DARK
    

ft.app(target=main)