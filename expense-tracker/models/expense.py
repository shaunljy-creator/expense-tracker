class Expense:
    def __init__(
        self,
        date,
        category,
        amount,
        currency,
        converted_amount,
        split_type="No Split",
        participants="You",
        notes="",
        id=None
    ):
        self.id = id
        self.date = date
        self.category = category
        self.amount = amount
        self.currency = currency
        self.converted_amount = converted_amount
        self.split_type = split_type
        self.participants = participants
        self.notes = notes

    def __repr__(self):
        return (
            f"Expense(id={self.id}, date={self.date}, category={self.category}, "
            f"amount={self.amount}, currency={self.currency}, "
            f"converted_amount={self.converted_amount}, split_type={self.split_type}, "
            f"participants={self.participants}, notes={self.notes})"
        )