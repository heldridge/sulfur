class ListPane:
    def __init__(self, term, items, width, height):
        self.term = term
        self.items = items
        self.current_item = 0
        self.width = width
        self.height = height
        self.offset = 0

    def get_item_string(self, item):
        return str(item)

    def render(self):
        # Draw top of box
        # Use width - 2 to account for the corners
        print(
            "\N{BOX DRAWINGS LIGHT DOWN AND RIGHT}"
            + "\N{BOX DRAWINGS LIGHT HORIZONTAL}" * (self.width - 2)
            + "\N{BOX DRAWINGS LIGHT DOWN AND LEFT}"
        )

        # Calculate where in our items list we will stop printing
        end_items = self.offset + self.height - 2
        # If we end before printing the last item, we have to print an ellipsis
        print_ellipsis = end_items < len(self.items)
        if print_ellipsis:
            # If we do print an ellipsis, that means we have to print one fewer item
            end_items -= 1

        # Print items
        for index, item in enumerate(self.items[self.offset : end_items]):
            item_string = self.get_item_string(item)

            if len(item_string) > self.width - 2:
                item_string = item_string[: self.width - 5] + "..."

            right_padding = self.width - 2 - len(item_string)

            if index + self.offset == self.current_item:
                item_string = self.term.underline(item_string)
            print(
                "\N{BOX DRAWINGS LIGHT VERTICAL}"
                + item_string
                + " " * right_padding
                + "\N{BOX DRAWINGS LIGHT VERTICAL}"
            )

        for _ in range(0, self.height - 2 - len(self.items)):
            print(
                "\N{BOX DRAWINGS LIGHT VERTICAL}"
                + " " * (self.width - 2)
                + "\N{BOX DRAWINGS LIGHT VERTICAL}"
            )

        if print_ellipsis:
            print(
                "\N{BOX DRAWINGS LIGHT VERTICAL}"
                + "..."
                + " " * (self.width - 5)
                + "\N{BOX DRAWINGS LIGHT VERTICAL}"
            )

        # Draw bottom of box
        print(
            "\N{BOX DRAWINGS LIGHT UP AND RIGHT}"
            + "\N{BOX DRAWINGS LIGHT HORIZONTAL}" * (self.width - 2)
            + "\N{BOX DRAWINGS LIGHT UP AND LEFT}"
        )

    def process_keystroke(self, val):
        if val.name == "KEY_UP":
            if self.offset > 0 and self.current_item == self.offset:
                # There is an offset and the current item is the top item on display
                self.offset -= 1

            if self.current_item > 0:
                self.current_item -= 1
        elif val.name == "KEY_DOWN":
            if self.offset + self.height - 2 < len(self.items):
                # There are hidden items
                if self.current_item == self.offset + self.height - 4:
                    # The current item is the bottom item in the display
                    self.offset += 1

            if self.current_item < len(self.items) - 1:
                self.current_item += 1
