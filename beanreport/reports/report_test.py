__copyright__ = "Copyright (C) 2014-2016  Martin Blais"
__license__ = "GNU GPLv2"

import unittest

from beanreport.utils import test_utils
from beanreport.reports import report
from beanreport.reports import base


class TestHelpReports(test_utils.TestCase):

    def test_get_list_report_string(self):
        help_string = report.get_list_report_string()
        self.assertTrue(help_string and isinstance(help_string, str))

    def test_get_list_report_string__invalid_report(self):
        help_string = report.get_list_report_string('blablabla')
        self.assertEqual(None, help_string)


class TestReportFunctions(unittest.TestCase):

    def test_get_all_report(self):
        all_reports = report.get_all_reports()
        self.assertTrue(all(issubclass(report_, base.Report)
                            for report_ in all_reports))


class TestScriptQuery(test_utils.TestCase):

    # pylint: disable=empty-docstring
    @test_utils.docfile
    def test_list_accounts_empty(self, filename):
        ""
        # Check that invocation with just a filename prints something (the list of reports).
        with test_utils.capture() as stdout:
            test_utils.run_with_args(report.main, [filename])
        self.assertTrue(stdout.getvalue())


class TestScriptPositions(test_utils.TestCase):

    @test_utils.docfile
    def test_success(self, filename):
        """
        2013-01-01 open Assets:Account1
        2013-01-01 open Assets:Account2
        2013-01-01 open Assets:Account3
        2013-01-01 open Equity:Unknown

        2013-04-05 *
          Equity:Unknown
          Assets:Account1     5000 USD

        2013-04-05 *
          Assets:Account1     -3000 USD
          Assets:Account2     30 BOOG {100 USD}

        2013-04-05 *
          Assets:Account1     -1000 USD
          Assets:Account3     800 EUR @ 1.25 USD
        """
        with test_utils.capture() as stdout:
            test_utils.run_with_args(report.main, [filename, 'holdings'])
        output = stdout.getvalue()
        self.assertTrue(test_utils.search_words('Assets:Account1 1,000.00 USD', output))
        self.assertTrue(test_utils.search_words('Assets:Account2    30.00 BOOG', output))
        self.assertTrue(test_utils.search_words('Assets:Account3   800.00 EUR', output))

    @test_utils.docfile
    def test_print_trial(self, filename):
        """
        2013-01-01 open Expenses:Restaurant
        2013-01-01 open Assets:Cash

        2014-03-02 * "Something"
          Expenses:Restaurant   50.02 USD
          Assets:Cash
        """
        with test_utils.capture() as stdout:
            test_utils.run_with_args(report.main, [filename, 'trial'])
        output = stdout.getvalue()
        self.assertLines("""
            Assets:Cash          -50.02 USD
            Equity
            Expenses:Restaurant   50.02 USD
            Income
            Liabilities
        """, output)

    # pylint: disable=empty-docstring
    @test_utils.docfile
    def test_print_trial_empty(self, filename):
        ""
        with test_utils.capture():
            test_utils.run_with_args(report.main, [filename, 'trial'])

if __name__ == '__main__':
    unittest.main()
