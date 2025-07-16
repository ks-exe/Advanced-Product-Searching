class Product:
    def __init__(self, pid, name, brand, price, availability, description, category, rating=0):
        self.pid = pid
        self.name = name
        self.brand = brand
        self.price = price
        self.availability = availability
        self.description = description
        self.category = category
        self.rating = rating  # Added for "top ratings"

    def __str__(self):
        return (f"[{self.pid}] {self.name} ({self.brand}) - Rs. {self.price} | {self.availability} | Rating: {self.rating}\n"
                f"{self.description} | Category: {self.category}\n")
    
    def __hash__(self):
        return hash(self.pid)  # Use pid as the unique identifier for hashing
    
    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        return self.pid == other.pid
    
    def __lt__(self, other):
        """Less than comparison based on price"""
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price
    
    def __gt__(self, other):
        """Greater than comparison based on price"""
        if not isinstance(other, Product):
            return NotImplemented
        return self.price > other.price
    
    def __le__(self, other):
        """Less than or equal comparison based on price"""
        if not isinstance(other, Product):
            return NotImplemented
        return self.price <= other.price
    
    def __ge__(self, other):
        """Greater than or equal comparison based on price"""
        if not isinstance(other, Product):
            return NotImplemented
        return self.price >= other.price 