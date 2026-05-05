from rctui import App, Component, Box, Text, Button, useState

class Counter(Component):
    def render(self):
        count, set_count = useState(0)
        
        return Box(
            flex_direction="column",
            align_items="center",
            justify_content="center",
            border="single",
            children=[
                Text(f"Count: {count}", style={"bold": True}),
                Button(
                    "Increment", 
                    on_click=lambda _: set_count(count + 1)
                )
            ]
        )

if __name__ == "__main__":
    app = App(Counter)
    app.run()
