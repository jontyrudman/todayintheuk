import poll.legislation.bills


class Bill(poll.legislation.bills.Bill):
    def as_html(self):
        """
        Represent bill as HTML.

        Element order:

        1. Title
        2. Origin
        3. Status
        4. Progress bar, if applicable
        """
        # TODO
        pass
