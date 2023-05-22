import requests
import pygame
import pygame_gui
from timeit import default_timer as timer


class Kitchen:
    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.resolution = (800, 600)
        self.selected_item_id = None
        self.monitor_delay = 2
        self.orders = self.get_orders()
        self.button_width = 150
        self.button_height = 100
        self.margin_x = 20
        self.margin_y = 20
        self.confirmation_dialog = None
        self.message_window = None
        self.update_order_names(init=True)
        self.init_pygame()
        self.init_ui()
        self.main()

    def get_orders(self):
        response = requests.get(f"{self.server_ip}/getOrders")
        data = response.json()
        return [item[0] for item in data]

    def update_order_names(self, order_index=None, init=False):
        new_names = list()
        for order in self.orders:
            items = self.get_ordered_items(order)
            text = f"NR {order}: "
            for item in items:
                text += f'{item[1]} {item[0]} '
            new_names.append(text.strip())
        self.order_names = new_names
        if not init:
            self.selection_list.set_item_list(self.order_names)
            if order_index != None:
                self.selection_list.item_list[order_index]['selected'] = True
                self.selection_list.item_list[order_index]['button_element'].select(
                )

    def update_orders(self):
        self.orders = self.get_orders()
        order_index = None
        if not self.selected_item_id in self.orders:
            self.selected_item_id = None
        else:
            order_index = self.orders.index(self.selected_item_id)
        self.update_order_names(order_index=order_index)

    def complete_order(self):
        msg, success = self.set_order_status(self.selected_item_id, 1)
        if success:
            self.orders = self.get_orders()
            self.update_order_names()
            self.selected_item_id = None
        return msg

    def get_ordered_items(self, order_id):
        url = f"{self.server_ip}/getOrderedItems/{order_id}"
        response = requests.get(url)
        return response.json()

    def set_order_status(self, order_id, status_code):
        url = f"{self.server_ip}/updateOrder/{order_id}"
        payload = f'status={status_code}'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("PUT", url, headers=headers, data=payload)
        self.set_order_info("Selected order info will appear here.")
        if response.status_code == 200:
            return response.text.strip(), True
        else:
            return "Failed to complete the order.", False

    def ask_if_sure_order(self):
        confirmation_dialog = pygame_gui.windows.UIConfirmationDialog(
            rect=pygame.Rect(
                (self.resolution[0] // 2 - 150, self.resolution[1] // 2 - 100), (300, 200)),
            manager=self.manager,
            window_title="Confirm order",
            action_long_desc=f"Are you sure you want to complete this order?",
            action_short_name="Yes",
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
        # Initialize pygame and create a window
        pygame.init()
        self.window = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption('KIT-CHEN')
        self.clock = pygame.time.Clock()

        # Create a GUI manager
        self.manager = pygame_gui.UIManager(self.resolution)
        self.manager.preload_fonts(
            [{'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])

    def set_order_info(self, msg):
        self.order_info.set_text(f"<body><font color=#E0E080><b>{msg}")

    def init_ui(self):
        # Create a selection list with the items
        self.selection_list = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((self.margin_x, self.margin_y), (400, 400)),
                                                                  item_list=self.order_names,
                                                                  manager=self.manager, allow_double_clicks=False)

        self.complete_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((self.resolution[0] - self.margin_x - self.button_width,
                                                                                       self.resolution[1] - self.margin_y - 50), (self.button_width, 50)),
                                                            text='Complete',
                                                            manager=self.manager)

        self.order_info = pygame_gui.elements.UITextBox(
            html_text="<body><font color=#E0E080><b>Selected order info will appear here.",
            relative_rect=pygame.Rect(
                (self.resolution[0] - 350, self.margin_y), (350, 400)),
            manager=self.manager)

    def main(self):
        running = True
        timer_start = timer()
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # pass the event to the UI manager
                self.manager.process_events(event)

                if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                    # If the selection list was changed
                    if event.ui_element == self.selection_list:
                        # Get the selected item id and text
                        if self.selection_list.get_single_selection() == None:
                            self.selected_item_id = None
                        else:
                            self.selected_item_id = self.orders[self.order_names.index(
                                self.selection_list.get_single_selection())]
                            selected_item_text = self.selection_list.get_single_selection()
                            # Print them to the console
                            print(
                                f'Selected item: {self.selected_item_id}, {selected_item_text}')
                            self.set_order_info(selected_item_text)

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.complete_button:
                        # Check if an item was selected
                        if self.selected_item_id is not None:
                            self.confirmation_dialog = self.ask_if_sure_order()
                            
                elif event.type == pygame_gui.UI_WINDOW_CLOSE:
                    if event.ui_element == self.confirmation_dialog:
                        self.confirmation_dialog.hide()
                    elif event.ui_element == self.message_window:
                        self.message_window.hide()
                elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
                    if event.ui_element == self.confirmation_dialog:
                        self.confirmation_dialog.hide()
                        print(f'Completing order for item: {self.selected_item_id}')
                        self.message_window = self.show_message_box(self.complete_order(),
                                                                    "Order Status", "OK")
            # Update the GUI manager
            self.manager.update(self.clock.tick(60))

            # draw the background
            self.window.fill(pygame.Color((44, 52, 58)))

            # Draw the GUI elements
            self.manager.draw_ui(self.window)

            # Update the display
            pygame.display.update()

            if timer_start + self.monitor_delay < timer():
                self.update_orders()
                timer_start = timer()


if __name__ == '__main__':
    server_ip = "http://127.0.0.1"
    Kitchen(server_ip)
