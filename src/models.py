from datetime import date, timedelta
import uuid
from typing import List, Optional

class RoomType:
    def __init__(self, name: str, capacity: int, nightly_price: float):
        self.name = name
        self.capacity = capacity
        self.nightly_price = nightly_price

class Room:
    def __init__(self, room_number: str, room_type: RoomType):
        self.room_number = room_number
        self.room_type = room_type
        self.bookings = []  # Will store a list of Bookings for this room

    def is_available(self, check_in: date, check_out: date) -> bool:
        # Part C: Check against date ranges of existing bookings
        for b in self.bookings:
            if b.status != "Cancelled":
                # Overlap logic: (Requested Check-In < Existing Check-Out) AND (Requested Check-Out > Existing Check-In)
                if check_in < b.check_out and check_out > b.check_in:
                    return False
        return True

class CancellationPolicy:
    def __init__(self, full_refund_hours: int, partial_refund_hours: int, partial_refund_percent: float):
        self.full_refund_hours = full_refund_hours
        self.partial_refund_hours = partial_refund_hours
        self.partial_refund_percent = partial_refund_percent

    def calculate_refund_amount(self, total_paid: float, check_in_date: date, cancel_date: date) -> float:
        # Calculate how many hours before check-in the cancellation occurred
        days_until_checkin = (check_in_date - cancel_date).days
        hours_until_checkin = days_until_checkin * 24

        if hours_until_checkin >= self.full_refund_hours:
            return total_paid
        elif hours_until_checkin >= self.partial_refund_hours:
            return total_paid * self.partial_refund_percent
        else:
            return 0.0

class Hotel:
    def __init__(self, hotel_id: str, name: str, city: str):
        self.hotel_id = hotel_id
        self.name = name
        self.city = city
        self.rooms: List[Room] = []
        # Hotel defines its own cancellation policy (e.g., 72 hours for full, 24 hours for 50%)
        self.cancellation_policy = CancellationPolicy(72, 24, 0.5)

    def add_room(self, room: Room):
        self.rooms.append(room)

    def get_available_rooms(self, check_in: date, check_out: date, room_type_name: str = None) -> List[Room]:
        available = []
        for r in self.rooms:
            # If a specific type is requested, filter by it. Otherwise just check availability.
            if (not room_type_name or r.room_type.name == room_type_name) and r.is_available(check_in, check_out):
                available.append(r)
        return available

class Customer:
    def __init__(self, customer_id: str, name: str, email: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.bookings = []

class Payment:
    def __init__(self, amount: float):
        self.payment_id = str(uuid.uuid4())
        self.amount = amount
        self.status = "Pending"

    def process(self) -> bool:
        # Simulated payment processing
        self.status = "Success"
        return True

class Refund:
    def __init__(self, amount: float):
        self.refund_id = str(uuid.uuid4())
        self.amount = amount
        self.status = "Processed"

class Voucher:
    def __init__(self, booking):
        self.voucher_id = str(uuid.uuid4())
        self.booking = booking
        self.issue_date = date.today()
    
    def __str__(self):
        return f"VOUCHER [{self.voucher_id}] | Hotel: {self.booking.hotel.name} | Room: {self.booking.room.room_number} | Dates: {self.booking.check_in} to {self.booking.check_out}"

class Booking:
    def __init__(self, customer: Customer, room: Room, check_in: date, check_out: date, hotel: Hotel):
        self.booking_id = str(uuid.uuid4())
        self.customer = customer
        self.room = room
        self.check_in = check_in
        self.check_out = check_out
        self.hotel = hotel
        
        # Calculate total price based on nightly rate and duration
        nights = (check_out - check_in).days
        self.total_price = nights * room.room_type.nightly_price
        
        self.status = "Pending"
        self.payment = None
        self.voucher = None
        self.refund = None

    def confirm_booking(self) -> bool:
        # Final availability check before charging
        if self.room.is_available(self.check_in, self.check_out):
            self.payment = Payment(self.total_price)
            if self.payment.process():
                self.status = "Confirmed"
                self.voucher = Voucher(self)
                self.room.bookings.append(self)
                self.customer.bookings.append(self)
                return True
        return False

    def cancel_booking(self, cancel_date: date) -> bool:
        if self.status == "Confirmed":
            refund_amount = self.hotel.cancellation_policy.calculate_refund_amount(
                self.payment.amount, self.check_in, cancel_date
            )
            self.refund = Refund(refund_amount)
            self.status = "Cancelled"
            return True
        return False
