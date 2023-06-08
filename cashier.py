# cashier script for the cafe
import pygame
import pygame_gui
import requests


def convertToCent(number):
    return f'{number/100:.2f}€'


class Cafe:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.resolution = (800, 600)
        # item columns
        self.columns = 4
        # button sizes and margins
        self.button_width = 150
        self.button_height = 100
        self.margin_x = (
            self.resolution[0] - self.columns * self.button_width) // (self.columns + 1)
        self.margin_y = 20
        self.init_pygame()
        self.items = self.get_items()
        self.setup_items_ui()
        self.main()

    def get_items(self):
        try:
            response = requests.get(f"{self.server_ip}/getItems")
            if response.status_code == 200:
                data = response.json()
                items = dict()
                for item in data:
                    items[item["Name"]] = dict()
                    items[item["Name"]]["ID"] = item["ID"]
                    items[item["Name"]]["Price"] = item["Price"]
                    items[item["Name"]]["Count"] = 0
                return items
            else:
                self.show_message_box(
                f"Error code {response.status_code}. Make sure the server is not broken.", "ERROR", "OK")
        except(requests.exceptions.ConnectionError):
            self.show_message_box(
                "Failed to connect to the server!\nTry restarting the program and/or verifying your network connectivity.", "ERROR", "OK")
            return dict()

    def update_price(self):
        price = price = sum(
            self.items[item]["Price"] * self.items[item]["Count"] for item in self.items)
        self.price_label.set_text(convertToCent(price))

    def add_order(self):
        order = '&'.join(
            f'{self.items[item]["ID"]}={self.items[item]["Count"]}' for item in self.items if self.items[item]["Count"] > 0)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        try:
            response = requests.request(
                "POST", f"{self.server_ip}/addOrder", headers=headers, data=order)
            if response.status_code == 200:
                order_id = response.text.strip()
                self.prev_order_label.set_text(f'Previous order {order_id}: {self.price_label.text}')
                self.reset_counts()
                return f'Order {order_id} was successfully placed!'
            elif response.status_code == 400:
                self.reset_counts()
                return "Invalid order! Make sure you select items."
            else:
                return "Failed to send order to the server!"
        except(requests.exceptions.ConnectionError):
            return "Failed to connect to the server!\nTry restarting the program and/or verifying your network connectivity."

    def reset_counts(self):
        for item in self.items:
            self.items[item]["Count"] = 0
            self.items[item]["CountLabel"].set_text("0")
        self.price_label.set_text("0.00€")

    def ask_if_sure_order(self):
        confirmation_dialog = pygame_gui.windows.UIConfirmationDialog(
            rect=pygame.Rect(
                (self.resolution[0] // 2 - 150, self.resolution[1] // 2 - 100), (300, 200)),
            manager=self.manager,
            window_title="Confirm order",
            action_long_desc=f"Are you sure you want to send this order, priced {self.price_label.text}?",
            action_short_name="Send",
        )
        return confirmation_dialog

    def show_message_box(self, message, title, confirm_text):
        message_window = pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect(
                            (self.resolution[0] // 2 - 150, self.resolution[1] // 2 - 100), (300, 250)),
            html_message=message,
            window_title=title,
            manager=self.manager)
        message_window.dismiss_button.set_text(
            confirm_text)
        return message_window

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption('CA-FE')
        self.setup_ui()

    def setup_ui(self):
        # create pygame gui stuff
        self.window = pygame.display.set_mode(self.resolution)
        self.manager = pygame_gui.UIManager(self.resolution)

        # button for ordering
        self.order_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.resolution[0] - self.margin_x - self.button_width,
                                       self.resolution[1] - self.margin_y - 50), (self.button_width, 50)),
            text="ORDER",
            manager=self.manager
        )

        # use disabled button for price because it looks nicer than a normal label and im lazy to do theming right now
        self.price_label = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.resolution[0] - self.margin_x - self.button_width*2,
                                       self.resolution[1] - self.margin_y - 50), (self.button_width, 50)),
            text="0.00€",
            manager=self.manager
        )
        self.price_label.disable()

        # same as before, but for showing previous order ID
        self.prev_order_label = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.margin_x,
                                       self.resolution[1] - self.margin_y - 50), (-1, 50)),
            text="No orders yet",
            manager=self.manager
        )
        self.prev_order_label.disable()

        # declare the message window variables
        self.message_window = None
        self.confirmation_dialog = None

    def setup_items_ui(self):
        for i, item in enumerate(self.items):
            # calculate the button position based on the index
            x = self.margin_x + (i % self.columns) * \
                (self.button_width + self.margin_x)
            y = self.margin_y + (i // self.columns) * \
                (self.button_height + self.margin_y)
            # create the name label
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((x, y), (-1, self.button_height)),
                text=item,
                manager=self.manager
            )
            # label for object count
            label = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(
                    (x + self.button_width - 10, y + self.button_height // 2 - 10), (20, 20)),
                text=str(self.items[item]["Count"]),
                manager=self.manager
            )
            # increment button
            plus_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(
                    (x + self.button_width - 20, y), (-1, 25)),
                text="+",
                manager=self.manager
            )
            # decrement button
            minus_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x, y), (-1, 25)),
                text="-",
                manager=self.manager
            )
            # add the buttons and labels to dict
            self.items[item]["CountLabel"] = label
            self.items[item]["IncBtn"] = plus_button
            self.items[item]["DecBtn"] = minus_button

    def main(self):
        # create a clock
        clock = pygame.time.Clock()
        # main loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # pass the event to the UI manager
                self.manager.process_events(event)

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.order_button:
                        self.confirmation_dialog = self.ask_if_sure_order()
                    else:
                        for item in self.items:
                            # check if the plus button is pressed
                            if event.ui_element == self.items[item]["IncBtn"]:
                                self.items[item]["Count"] += 1
                                self.items[item]["CountLabel"].set_text(
                                    str(self.items[item]["Count"]))
                                self.update_price()
                            # check if the minus button is pressed
                            elif event.ui_element == self.items[item]["DecBtn"]:
                                if self.items[item]["Count"] != 0:
                                    self.items[item]["Count"] -= 1
                                    self.items[item]["CountLabel"].set_text(
                                        str(self.items[item]["Count"]))
                                    self.update_price()
                elif event.type == pygame_gui.UI_WINDOW_CLOSE:
                    if event.ui_element == self.confirmation_dialog:
                        self.confirmation_dialog.hide()
                    elif event.ui_element == self.message_window:
                        self.message_window.hide()
                elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    if event.ui_element == self.confirmation_dialog:
                        self.confirmation_dialog.hide()
                        self.message_window = self.show_message_box(self.add_order(),
                                                                    "Order Status", "OK")
            # update the UI manager
            self.manager.update(clock.tick(60))

            # draw the background
            self.window.fill(pygame.Color((44, 52, 58)))

        # draw a border around each item
            border_color = (26, 105, 135)
            border_width = 2  # pixels
            for i in range(len(self.items)):
                x = self.margin_x + (i % self.columns) * \
                    (self.button_width + self.margin_x) - 10
                y = self.margin_y + (i // self.columns) * \
                    (self.button_height + self.margin_y) - 10
                w = self.button_width + 40
                h = self.button_height + 20
                border_rect = pygame.Rect(
                    x - border_width // 2, y - border_width // 2, w + border_width, h + border_width)
                pygame.draw.rect(self.window, border_color,
                                 border_rect, border_width)

            # draw the UI
            self.manager.draw_ui(self.window)
            # update the display
            pygame.display.update()

        # quit when done
        pygame.quit()


if __name__ == '__main__':
    server_ip = "http://127.0.0.1"
    Cafe(server_ip)
