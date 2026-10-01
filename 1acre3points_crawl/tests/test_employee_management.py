import unittest

from practice.anthropic.employee_management import EmployeeManagement, solution


class EmployeeManagementTests(unittest.TestCase):
    def test_level_1_and_2(self):
        self.assertEqual(
            solution(
                [
                    ["ADD_WORKER", "Zoe", "Dev", "10"],
                    ["ADD_WORKER", "Amy", "Dev", "10"],
                    ["ADD_WORKER", "Amy", "Dev", "99"],
                    ["REGISTER", "Zoe", "10"],
                    ["REGISTER", "Zoe", "20"],
                    ["REGISTER", "Amy", "30"],
                    ["REGISTER", "Amy", "40"],
                    ["GET", "Zoe"],
                    ["TOP_N_WORKERS", "2", "Dev"],
                ]
            ),
            [
                "true",
                "true",
                "false",
                "registered",
                "registered",
                "registered",
                "registered",
                "10",
                "Amy(10), Zoe(10)",
            ],
        )

    def test_promotion_waits_for_first_eligible_entry(self):
        office = EmployeeManagement()
        self.assertEqual(office.add_worker("A", "Junior", 10), "true")
        office.register("A", 0)
        office.register("A", 10)

        self.assertEqual(office.promote("A", "Senior", 20, 100), "success")
        self.assertEqual(office.promote("A", "Staff", 30, 110), "invalid_request")

        # This entire session is before the promotion's start time.
        office.register("A", 50)
        office.register("A", 60)
        self.assertEqual(office.top_n_workers(1, "Junior"), "A(20)")

        office.register("A", 100)
        office.register("A", 110)
        self.assertEqual(office.top_n_workers(1, "Senior"), "A(30)")
        self.assertEqual(office.calc_salary("A", 0, 200), "400")

    def test_overlapping_double_pay_is_counted_only_once(self):
        office = EmployeeManagement()
        office.add_worker("A", "Dev", 10)
        office.register("A", 0)
        office.register("A", 40)
        office.set_double_paid(5, 25)
        office.set_double_paid(20, 35)

        self.assertEqual(office.double_paid, [(5, 35)])
        self.assertEqual(office.calc_salary("A", 0, 40), "700")
        self.assertEqual(office.calc_salary("A", 20, 30), "200")

    def test_unfinished_session_does_not_count(self):
        office = EmployeeManagement()
        self.assertEqual(office.get("missing"), "-1")
        office.add_worker("A", "Dev", 10)
        office.register("A", 5)
        self.assertEqual(office.get("A"), "0")
        self.assertEqual(office.calc_salary("A", 0, 100), "0")


if __name__ == "__main__":
    unittest.main()
