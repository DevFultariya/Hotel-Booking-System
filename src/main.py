import sys
from datetime import date, timedelta
from models import Hotel, RoomType, Room, Customer, Booking

def init_data():
    """Initializes the system with sample data for testing."""
    h1 = Hotel("H1", "Grand Plaza", "New York")
    h2 = Hotel("H2", "Oceanview Resort", "Miami")
    h3 = Hotel("H3", "Mountain Retreat", "Denver")
    
    # Setup room types
    std_type = RoomType("Standard", 2, 100.0)
    dlx_type = RoomType("Deluxe", 3, 200.0)
    ste_type = RoomType("Suite", 4, 350.0)
    
    # Add rooms to hotels
    h1.add_room(Room("101", std_type))
    h1.add_room(Room("201", dlx_type))
    
    h2.add_room(Room("101", std_type))
    h2.add_room(Room("301", ste_type))

    h3.add_room(Room("101", std_type))
    h3.add_room(Room("201", dlx_type))
    h3.add_room(Room("301", ste_type))
    
    # Setup dummy customer
    customer = Customer("C1", "Alice Smith", "alice@example.com")
    
    return [h1, h2, h3], [std_type, dlx_type, ste_type], customer

def run_test_cases():
    print("\n" + "="*40)
    print("--- Running Required Test Cases ---")
    print("="*40)
    today = date.today()
    
    # Create a dummy customer for tests so we don't pollute the CLI user's list
    customer = Customer("TC", "Test Customer", "test@example.com")
    
    # Create an isolated hotel specifically for tests so manual testing doesn't interfere
    test_hotel = Hotel("TEST", "Test Hotel", "Test City")
    rtype = RoomType("Standard", 2, 100.0)
    r1 = Room("101", rtype)
    test_hotel.add_room(r1)
    
    # TC01: Successful booking
    b1 = Booking(customer, r1, today + timedelta(days=10), today + timedelta(days=12), test_hotel)
    success = b1.confirm_booking()
    if success and b1.status == "Confirmed" and b1.voucher:
        print("TC01 Successful booking: PASS")
    else:
        print("TC01 Successful booking: FAIL")

    # TC02: Overlapping booking
    b2 = Booking(customer, r1, today + timedelta(days=11), today + timedelta(days=13), test_hotel)
    success = b2.confirm_booking()
    if not success and b2.status == "Pending":
        print("TC02 Overlapping booking: PASS")
    else:
        print("TC02 Overlapping booking: FAIL")

    # TC03: Payment failure
    b3 = Booking(customer, r1, today + timedelta(days=20), today + timedelta(days=22), test_hotel)
    # Temporarily mock the payment process to fail
    import models
    original_process = models.Payment.process
    models.Payment.process = lambda self: False
    success = b3.confirm_booking()
    if not success and b3.status == "Pending" and not b3.voucher:
        print("TC03 Payment failure: PASS")
    else:
        print("TC03 Payment failure: FAIL")
    # Restore original method
    models.Payment.process = original_process

    # TC04: Cancellation, full refund
    # We create a booking and cancel it > 72 hours before check-in
    b4 = Booking(customer, r1, today + timedelta(days=5), today + timedelta(days=7), test_hotel)
    b4.confirm_booking()
    # Cancel 4 days (96 hours) before checkin (Full refund > 72 hours)
    success = b4.cancel_booking(today + timedelta(days=1))
    if success and b4.status == "Cancelled" and b4.refund.amount == b4.total_price:
        print(f"TC04 Cancellation, full refund: PASS (Refunded ${b4.refund.amount})")
    else:
        print("TC04 Cancellation, full refund: FAIL")

    # TC05: Cancellation, partial or no refund
    b5 = Booking(customer, r1, today + timedelta(days=5), today + timedelta(days=7), test_hotel)
    b5.confirm_booking()
    # Cancel 2 days (48 hours) before checkin (Partial refund between 24-72 hours)
    success = b5.cancel_booking(today + timedelta(days=3))
    expected_refund = b5.total_price * test_hotel.cancellation_policy.partial_refund_percent
    if success and b5.status == "Cancelled" and b5.refund.amount == expected_refund:
        print(f"TC05 Cancellation, partial or no refund: PASS (Refunded ${b5.refund.amount})")
    else:
        print("TC05 Cancellation, partial or no refund: FAIL")

    # TC06: Non-overlapping dates
    # Book exactly when a previous one ends (b1 was booked days 10 to 12. Book days 12 to 14)
    b6 = Booking(customer, r1, today + timedelta(days=12), today + timedelta(days=14), test_hotel)
    success = b6.confirm_booking()
    if success:
        print("TC06 Non-overlapping dates: PASS")
    else:
        print("TC06 Non-overlapping dates: FAIL")

    # TC07: Invalid room
    room_number_input = "999"
    selected_room = next((r for r in test_hotel.rooms if r.room_number == room_number_input), None)
    if not selected_room:
        print("TC07 Invalid room: PASS")
    else:
        print("TC07 Invalid room: FAIL")
    
    print("="*40 + "\n")

def main():
    hotels, room_types, customer = init_data()
    
    while True:
        print("\n" + "="*30)
        print(" Hotel Room Booking CLI System")
        print("="*30)
        print("1. View Hotels")
        print("2. View Room Types")
        print("3. View Available Rooms (for a date range)")
        print("4. Book a Room")
        print("5. View My Bookings")
        print("6. Cancel Booking")
        print("7. Run Required Test Cases")
        print("8. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            print("\n[HOTELS]")
            for h in hotels:
                print(f"- {h.name} located in {h.city}")
        
        elif choice == '2':
            print("\n[ROOM TYPES]")
            for rt in room_types:
                print(f"- {rt.name} | Capacity: {rt.capacity} | Price: ${rt.nightly_price}/night")
        
        elif choice == '3':
            try:
                ci_str = input("Enter Check-in Date (YYYY-MM-DD): ")
                co_str = input("Enter Check-out Date (YYYY-MM-DD): ")
                ci = date.fromisoformat(ci_str)
                co = date.fromisoformat(co_str)
                print("\n[AVAILABLE ROOMS]")
                found_any = False
                for h in hotels:
                    rooms = h.get_available_rooms(ci, co)
                    if rooms:
                        print(f"--- {h.name} ({h.city}) ---")
                        for r in rooms:
                            print(f"  - Room {r.room_number} ({r.room_type.name}) - ${r.room_type.nightly_price}/night")
                        found_any = True
                if not found_any:
                    print("No rooms available for those dates.")
            except ValueError:
                print("\nError: Please enter dates in correct YYYY-MM-DD format.")
        
        elif choice == '4':
            try:
                ci_str = input("Enter Check-in Date (YYYY-MM-DD): ")
                co_str = input("Enter Check-out Date (YYYY-MM-DD): ")
                ci = date.fromisoformat(ci_str)
                co = date.fromisoformat(co_str)
                
                hotel_name = input("Enter Hotel Name: ")
                hotel = next((h for h in hotels if h.name.lower() == hotel_name.lower()), None)
                if not hotel:
                    print("\nError: Invalid Hotel Name.")
                    continue

                room_num = input("Enter Room Number to book: ")
                room = next((r for r in hotel.rooms if r.room_number == room_num), None)
                if not room:
                    print("\nError: Invalid Room Number for this hotel.")
                    continue
                
                user_id = input("Please enter your ID (Passport/Driving License): ")
                
                nights = (co - ci).days
                if nights <= 0:
                    print("\nError: Check-out date must be after check-in date.")
                    continue
                
                total_price = nights * room.room_type.nightly_price
                
                print(f"\n[BOOKING SUMMARY]")
                print(f"Hotel: {hotel.name}")
                print(f"Room: {room.room_number} ({room.room_type.name})")
                print(f"Dates: {ci} to {co} ({nights} nights)")
                print(f"Total Price: ${total_price:.2f}")
                print(f"ID Verified: {user_id}")
                
                confirm = input("\nDo you want to confirm and pay? (y/n): ")
                if confirm.lower() == 'y':
                    b = Booking(customer, room, ci, co, hotel)
                    b.guest_id = user_id
                    if b.confirm_booking():
                        print("\nSuccess! Payment processed and Booking Confirmed.")
                        print(b.voucher)
                    else:
                        print("\nFailed! Room is already booked for those dates.")
                else:
                    print("\nBooking cancelled by user.")
                    
            except ValueError:
                print("\nError: Please enter dates in correct YYYY-MM-DD format.")
                
        elif choice == '5':
            print(f"\n[MY BOOKINGS for {customer.name}]")
            has_active = False
            for i, b in enumerate(customer.bookings):
                if b.status == "Confirmed":
                    print(f"[{i}] Room {b.room.room_number} at {b.hotel.name} | {b.check_in} to {b.check_out} | Status: {b.status}")
                    has_active = True
            if not has_active:
                print("No confirmed bookings found.")
                
        elif choice == '6':
            try:
                idx = int(input("Enter the booking index to cancel: "))
                if 0 <= idx < len(customer.bookings):
                    b = customer.bookings[idx]
                    cancel_date = date.today()
                    
                    if b.status != "Confirmed":
                        print("\nBooking is not confirmed or already cancelled.")
                        continue
                    
                    refund_amount = b.hotel.cancellation_policy.calculate_refund_amount(
                        b.payment.amount, b.check_in, cancel_date
                    )
                    
                    print(f"\n[CANCELLATION SUMMARY]")
                    print(f"Total Paid: ${b.payment.amount:.2f}")
                    print(f"Refund Amount: ${refund_amount:.2f}")
                    
                    confirm = input("\nAre you sure you want to cancel? (y/n): ")
                    if confirm.lower() == 'y':
                        if b.cancel_booking(cancel_date):
                            print(f"\nSuccess! Booking cancelled. A refund of ${b.refund.amount:.2f} has been processed back to your account.")
                        else:
                            print("\nFailed! Could not cancel booking.")
                    else:
                        print("\nCancellation aborted.")
                else:
                    print("\nError: Invalid index.")
            except ValueError:
                print("\nError: Please enter a valid number.")
                
        elif choice == '7':
            run_test_cases()
            
        elif choice == '8':
            print("\nExiting system...")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please pick 1-8.")

if __name__ == "__main__":
    main()
