# Hotel Booking System (Lab 7)

An Object-Oriented Command Line Interface (CLI) application that simulates a hotel room booking system. This project demonstrates core Software Engineering concepts including Requirement Analysis, UML Design, and OOP implementation.

## Features

- **Multi-Hotel Management:** Supports multiple hotels across different cities.
- **Smart Room Availability:** Date-range based availability checking prevents double booking overlapping dates while allowing back-to-back bookings.
- **Booking & Checkout:** Simulates payment processing and generates confirmation vouchers.
- **Tiered Cancellation Policy:** Automatically calculates refunds based on proximity to the check-in date:
  - `> 72 hours`: 100% Full Refund
  - `24 - 72 hours`: 50% Partial Refund
  - `< 24 hours`: No Refund
- **Automated Test Driver:** Includes an automated test suite verifying edge cases (TC01 to TC07).

## Project Structure

```text
├── src/
│   ├── models.py       # Core classes (Hotel, Room, Booking, Customer, etc.)
│   └── main.py         # The CLI entry point and Automated Test Driver
├── Lab7_Report.pdf     # Requirement Analysis & Relationships (Parts A, B, C)
├── Lab7_UML.pdf        # Complete UML Class Diagram (Part D)
└── Lab7_RunInstructions.txt
```

## How to Run

1. Ensure you have **Python 3.6+** installed.
2. Clone this repository.
3. Open your terminal and navigate to the `src` directory:
   ```bash
   cd src
   ```
4. Run the main driver file:
   ```bash
   python main.py
   ```
5. Follow the on-screen interactive menu to view hotels, book rooms, or cancel bookings!

## Running the Tests

From the main menu, press **`7`** to run the Required Test Cases. The system will automatically spawn an isolated test environment, execute TC01 through TC07, and output the `PASS/FAIL` status of each scenario.
