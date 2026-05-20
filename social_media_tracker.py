"""
=============================================================
  SOCIAL MEDIA USAGE TRACKER AND LIMITER
  A Beginner/Intermediate Python Project
  Covers: OOP, Flow Control, Functions, Collections, File & Exception Handling
=============================================================
"""

import json                  # For reading/writing JSON data files
import os                    # For file existence checks
import datetime              # For getting current date and time

# ─────────────────────────────────────────────────────────────
#  CO1: OOP — Classes and Constructors
# ─────────────────────────────────────────────────────────────

class SocialMediaApp:
    """Represents a single social media application being tracked."""

    def __init__(self, name, daily_limit_minutes):
        """Constructor: initialises app name, limit, and usage."""
        self.name = name                          # App name (e.g., "Instagram")
        self.daily_limit_minutes = daily_limit_minutes  # User-set daily limit
        self.usage_today = 0                      # Minutes used today

    def add_usage(self, minutes):
        """CO3: Function — adds usage time to the app."""
        if minutes > 0:                           # CO2: Condition
            self.usage_today += minutes
        else:
            print("  ⚠  Usage time must be positive.")

    def is_limit_exceeded(self):
        """CO2: Condition — returns True if daily limit is exceeded."""
        return self.usage_today >= self.daily_limit_minutes

    def remaining_time(self):
        """CO3: Function — calculates remaining allowed time."""
        remaining = self.daily_limit_minutes - self.usage_today
        return max(0, remaining)                  # CO2: never return negative

    def status_message(self):
        """CO3: String operation — returns a status string."""
        percent = (self.usage_today / self.daily_limit_minutes) * 100
        bar_filled = int(percent // 5)            # 20-char progress bar
        bar = "█" * bar_filled + "░" * (20 - bar_filled)
        return (f"  {self.name:<12} | Used: {self.usage_today:>4} min"
                f" | Limit: {self.daily_limit_minutes:>4} min"
                f" | [{bar}] {percent:5.1f}%")


class UsageTracker:
    """Main tracker: manages multiple apps, file I/O, and reports."""

    # CO4: Class-level list of default apps
    DEFAULT_APPS = ["Instagram", "YouTube", "WhatsApp", "Facebook", "Twitter", "Snapchat"]

    def __init__(self, username):
        """Constructor: sets up tracker for a specific user."""
        self.username = username                  # User's name
        self.apps = {}                            # CO4: Dictionary  {app_name: SocialMediaApp}
        self.history = []                         # CO4: List of past session records
        self.data_file = f"{username}_data.json"  # CO5: File handling
        self._load_data()                         # Load saved data on startup

    # ── File Handling (CO5) ─────────────────────────────────

    def _load_data(self):
        """CO5: File Handling — loads user data from JSON file."""
        try:                                      # CO5: Exception handling
            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                # Rebuild app objects from saved dictionary
                for app_name, app_data in data.get("apps", {}).items():
                    app = SocialMediaApp(app_name, app_data["limit"])
                    app.usage_today = app_data["usage_today"]
                    self.apps[app_name] = app
                self.history = data.get("history", [])
                print(f"\n  ✔ Data loaded for '{self.username}'.")
            else:
                print(f"\n  ℹ  No existing data. Starting fresh for '{self.username}'.")
        except json.JSONDecodeError:
            print("  ✖  Data file is corrupted. Starting fresh.")  # CO5: Specific exception
        except PermissionError:
            print("  ✖  Cannot read data file. Check permissions.")
        except Exception as e:                    # CO5: Generic exception catch
            print(f"  ✖  Unexpected error loading data: {e}")

    def _save_data(self):
        """CO5: File Handling — saves current state to JSON file."""
        try:
            data = {
                "username": self.username,
                "apps": {
                    name: {
                        "limit": app.daily_limit_minutes,
                        "usage_today": app.usage_today
                    }
                    for name, app in self.apps.items()  # Dictionary comprehension
                },
                "history": self.history
            }
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=4)      # Write pretty JSON
        except IOError as e:
            print(f"  ✖  Could not save data: {e}")  # CO5: IOError handling

    # ── App Management ──────────────────────────────────────

    def add_app(self, app_name, limit_minutes):
        """CO3: Function — adds a new app to track."""
        app_name = app_name.strip().title()       # CO3: String operation
        if app_name in self.apps:                 # CO2: Condition
            print(f"  ℹ  '{app_name}' is already being tracked.")
        elif limit_minutes <= 0:                  # CO2: Validation condition
            print("  ⚠  Limit must be greater than 0 minutes.")
        else:
            self.apps[app_name] = SocialMediaApp(app_name, limit_minutes)
            print(f"  ✔ Added '{app_name}' with a {limit_minutes}-min daily limit.")
            self._save_data()

    def log_usage(self, app_name, minutes):
        """CO3: Function — logs usage time for a given app."""
        app_name = app_name.strip().title()
        if app_name not in self.apps:             # CO2: Condition
            print(f"  ✖  '{app_name}' not found. Add it first.")
            return

        app = self.apps[app_name]
        app.add_usage(minutes)

        # CO4: Build a record tuple and append to history list
        record = {
            "date": str(datetime.date.today()),
            "app": app_name,
            "minutes": minutes,
            "total_today": app.usage_today
        }
        self.history.append(record)               # CO4: List append

        # CO2: Conditional warning system
        if app.is_limit_exceeded():
            print(f"\n  🚨 LIMIT EXCEEDED for {app_name}!")
            print(f"     You've used {app.usage_today} min (limit: {app.daily_limit_minutes} min).")
        elif app.usage_today >= app.daily_limit_minutes * 0.8:
            print(f"\n  ⚠  WARNING: You've used 80%+ of your {app_name} limit today.")
            print(f"     Remaining: {app.remaining_time()} min.")
        else:
            print(f"  ✔ Logged {minutes} min on {app_name}. Remaining today: {app.remaining_time()} min.")

        self._save_data()

    def reset_daily_usage(self):
        """Resets today's usage for all apps (to be called each new day)."""
        for app in self.apps.values():            # Iterate dictionary values
            app.usage_today = 0
        print("  ✔ Daily usage reset for all apps.")
        self._save_data()

    # ── Display & Reports ────────────────────────────────────

    def show_all_apps(self):
        """CO3: Function — displays status of all tracked apps."""
        if not self.apps:                         # CO2: Condition
            print("  ℹ  No apps tracked yet. Add some first.")
            return

        print("\n" + "═" * 65)
        print(f"  📊 TODAY'S USAGE — {self.username}  ({datetime.date.today()})")
        print("═" * 65)
        for app in self.apps.values():            # CO4: Iterate dictionary
            print(app.status_message())
            if app.is_limit_exceeded():           # CO2: Condition
                print(f"  {'':12}   ⛔ LIMIT EXCEEDED")
        print("═" * 65)

    def daily_report(self):
        """CO3: Function — generates a daily usage summary report."""
        print("\n" + "─" * 55)
        print("  📅 DAILY REPORT")
        print("─" * 55)

        if not self.apps:
            print("  No data to report.")
            return

        total_minutes = sum(app.usage_today for app in self.apps.values())  # CO3: sum
        exceeded_apps = [name for name, app in self.apps.items()
                         if app.is_limit_exceeded()]         # CO4: List comprehension
        safe_apps = [name for name, app in self.apps.items()
                     if not app.is_limit_exceeded()]         # CO4: List comprehension

        print(f"  User          : {self.username}")
        print(f"  Date          : {datetime.date.today()}")
        print(f"  Total usage   : {total_minutes} minutes ({total_minutes/60:.1f} hours)")
        print(f"  Apps tracked  : {len(self.apps)}")
        print(f"  Limits exceeded: {', '.join(exceeded_apps) if exceeded_apps else 'None ✔'}")
        print(f"  Within limits : {', '.join(safe_apps) if safe_apps else 'None'}")
        print("─" * 55)

        # Identify the most-used app — CO4: dictionary + max()
        if self.apps:
            top_app = max(self.apps.values(), key=lambda a: a.usage_today)
            print(f"  Most used app : {top_app.name} ({top_app.usage_today} min)")
        print("─" * 55)

        # CO5: Write report to file
        try:
            report_file = f"{self.username}_daily_report.txt"
            with open(report_file, "a") as f:     # Append mode
                f.write(f"\n{'='*40}\n")
                f.write(f"Report Date  : {datetime.datetime.now()}\n")
                f.write(f"Total usage  : {total_minutes} min\n")
                f.write(f"Exceeded     : {exceeded_apps}\n")
                for app in self.apps.values():
                    f.write(f"  {app.name}: {app.usage_today}/{app.daily_limit_minutes} min\n")
            print(f"  ✔ Report saved to '{report_file}'.")
        except IOError as e:
            print(f"  ✖  Could not write report file: {e}")

    def weekly_summary(self):
        """CO3, CO4: Function — summarises the last 7 days from history."""
        print("\n" + "─" * 55)
        print("  📆 WEEKLY SUMMARY (last 7 days)")
        print("─" * 55)

        if not self.history:
            print("  No history available yet.")
            return

        today = datetime.date.today()
        week_ago = str(today - datetime.timedelta(days=7))

        # CO4: Filter history list using a condition
        recent = [r for r in self.history if r["date"] >= week_ago]

        if not recent:
            print("  No activity in the last 7 days.")
            return

        # CO4: Dictionary to accumulate per-app totals
        app_totals = {}
        for record in recent:                     # CO2: Loop + condition
            app = record["app"]
            app_totals[app] = app_totals.get(app, 0) + record["minutes"]

        # CO4: Set of unique dates active
        active_dates = {record["date"] for record in recent}  # CO4: Set

        print(f"  Active days   : {len(active_dates)}/7")
        print(f"  Total sessions: {len(recent)}")
        print()
        print(f"  {'App':<14} | {'Total (min)':>11} | {'Daily avg':>9}")
        print(f"  {'─'*14}-+-{'─'*11}-+-{'─'*9}")
        for app, total in sorted(app_totals.items(), key=lambda x: -x[1]):
            avg = total / max(len(active_dates), 1)
            print(f"  {app:<14} | {total:>11} | {avg:>8.1f}")
        print("─" * 55)


# ─────────────────────────────────────────────────────────────
#  CO3: Functions for menu display
# ─────────────────────────────────────────────────────────────

def print_banner():
    """Prints the application header banner."""
    print("\n" + "╔" + "═"*61 + "╗")
    print("║" + "  📱 SOCIAL MEDIA USAGE TRACKER & LIMITER".center(61) + "║")
    print("║" + "  Beginner Python Project  |  All COs Covered".center(61) + "║")
    print("╚" + "═"*61 + "╝")


def print_menu():
    """CO3: Function — prints the main menu."""
    print("\n  ┌─────────────────────────────────────────┐")
    print("  │              MAIN MENU                  │")
    print("  ├─────────────────────────────────────────┤")
    print("  │  1. Add / configure an app              │")
    print("  │  2. Log usage for an app                │")
    print("  │  3. View today's usage                  │")
    print("  │  4. Daily report                        │")
    print("  │  5. Weekly summary                      │")
    print("  │  6. Reset today's usage                 │")
    print("  │  7. Quick-add default apps              │")
    print("  │  8. Exit                                │")
    print("  └─────────────────────────────────────────┘")


def get_valid_integer(prompt, min_val=1, max_val=9999):
    """CO3, CO5: Function with exception handling — gets a validated integer."""
    while True:                                   # CO2: Loop until valid input
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:       # CO2: Range condition
                return value
            else:
                print(f"  ⚠  Please enter a number between {min_val} and {max_val}.")
        except ValueError:                        # CO5: Exception for non-numeric input
            print("  ✖  Invalid input. Please enter a whole number.")


def get_app_choice(tracker):
    """CO4: Function — lets user pick from tracked apps or type a new name."""
    if tracker.apps:                              # CO2: Condition
        print("\n  Tracked apps:")
        # CO4: Enumerate a list
        app_list = list(tracker.apps.keys())      # CO4: Convert dict keys to list
        for i, name in enumerate(app_list, 1):
            print(f"    {i}. {name}")
        print("    0. Type a custom name")

        choice = get_valid_integer("  Choose (0 for custom): ", 0, len(app_list))
        if choice == 0:
            return input("  App name: ").strip()
        else:
            return app_list[choice - 1]           # CO4: List index access
    else:
        return input("  App name: ").strip()


# ─────────────────────────────────────────────────────────────
#  Main program — Menu-driven loop (CO2)
# ─────────────────────────────────────────────────────────────

def main():
    """Entry point — runs the menu-driven application."""
    print_banner()

    # Get username with validation
    while True:
        username = input("\n  Enter your name: ").strip()
        if username:                              # CO2: Non-empty check
            break
        print("  ⚠  Name cannot be empty.")

    tracker = UsageTracker(username)              # CO1: Create object

    # CO2: Main application loop
    while True:
        print_menu()
        choice = get_valid_integer("  Your choice (1-8): ", 1, 8)

        # ── Option 1: Add app ────────────────────────────
        if choice == 1:
            print("\n  ADD / CONFIGURE APP")
            app_name = input("  App name (e.g., Instagram): ").strip()
            limit = get_valid_integer("  Daily limit in minutes: ", 1, 1440)
            tracker.add_app(app_name, limit)

        # ── Option 2: Log usage ──────────────────────────
        elif choice == 2:
            print("\n  LOG USAGE")
            if not tracker.apps:
                print("  ℹ  No apps yet. Add an app first (Option 1).")
            else:
                app_name = get_app_choice(tracker)
                minutes = get_valid_integer("  Minutes used: ", 1, 1440)
                tracker.log_usage(app_name, minutes)

        # ── Option 3: View today ─────────────────────────
        elif choice == 3:
            tracker.show_all_apps()

        # ── Option 4: Daily report ───────────────────────
        elif choice == 4:
            tracker.daily_report()

        # ── Option 5: Weekly summary ─────────────────────
        elif choice == 5:
            tracker.weekly_summary()

        # ── Option 6: Reset daily usage ──────────────────
        elif choice == 6:
            confirm = input("  Reset ALL today's usage? (yes/no): ").strip().lower()
            if confirm == "yes":                  # CO2: String condition
                tracker.reset_daily_usage()
            else:
                print("  Reset cancelled.")

        # ── Option 7: Quick-add defaults ─────────────────
        elif choice == 7:
            print("\n  Quick-adding default apps with 30-min limits...")
            for app_name in UsageTracker.DEFAULT_APPS:  # CO4: Iterate class-level list
                if app_name not in tracker.apps:  # CO2: Condition
                    tracker.add_app(app_name, 30)
            print("  ✔ Done! You can change limits using Option 1.")

        # ── Option 8: Exit ────────────────────────────────
        elif choice == 8:
            print("\n  Goodbye! Stay mindful of your screen time. 👋\n")
            break                                 # CO2: Exit loop


# Standard Python entry point guard
if __name__ == "__main__":
    main()
