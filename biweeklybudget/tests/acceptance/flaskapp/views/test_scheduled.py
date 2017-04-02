"""
The latest version of this package is available at:
<http://github.com/jantman/biweeklybudget>

################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of biweeklybudget, also known as biweeklybudget.

    biweeklybudget is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    biweeklybudget is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with biweeklybudget.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/biweeklybudget> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

import pytest
from datetime import timedelta
from selenium.webdriver.support.ui import Select

from biweeklybudget.utils import dtnow
from biweeklybudget.tests.acceptance_helpers import AcceptanceHelper
from biweeklybudget.models.scheduled_transaction import ScheduledTransaction


@pytest.mark.acceptance
class TestSchedTrans(AcceptanceHelper):

    @pytest.fixture(autouse=True)
    def get_page(self, base_url, selenium, testflask, refreshdb):  # noqa
        self.baseurl = base_url
        selenium.get(base_url + '/scheduled')

    def test_heading(self, selenium):
        heading = selenium.find_element_by_class_name('navbar-brand')
        assert heading.text == 'Scheduled Transactions - BiweeklyBudget'

    def test_nav_menu(self, selenium):
        ul = selenium.find_element_by_id('side-menu')
        assert ul is not None
        assert 'nav' in ul.get_attribute('class')
        assert ul.tag_name == 'ul'

    def test_notifications(self, selenium):
        div = selenium.find_element_by_id('notifications-row')
        assert div is not None
        assert div.get_attribute('class') == 'row'


@pytest.mark.acceptance
class TestSchedTransDefault(AcceptanceHelper):

    @pytest.fixture(autouse=True)
    def get_page(self, base_url, selenium, testflask, refreshdb):  # noqa
        self.baseurl = base_url
        self.dt = dtnow()
        selenium.get(base_url + '/scheduled')

    def test_table(self, selenium):
        table = selenium.find_element_by_id('table-scheduled-txn')
        texts = self.tbody2textlist(table)
        elems = self.tbody2elemlist(table)
        assert texts == [
            [
                'yes',
                'per period',
                '1 per period',
                '$-333.33',
                'ST3',
                'BankTwoStale (2)',
                'Standing1 (4)'
            ],
            [
                'yes',
                'monthly',
                '4th',
                '$222.22',
                'ST2',
                'BankOne (1)',
                'Periodic2 (2)'
            ],
            [
                'yes',
                'date',
                (self.dt + timedelta(days=4)).date().strftime('%Y-%m-%d'),
                '$111.11',
                'ST1',
                'BankOne (1)',
                'Periodic1 (1)'
            ],
            [
                'NO',
                'per period',
                '3 per period',
                '$666.66',
                'ST6',
                'BankTwoStale (2)',
                'Standing1 (4)'
            ],
            [
                'NO',
                'monthly',
                '5th',
                '$555.55',
                'ST5',
                'BankOne (1)',
                'Periodic2 (2)'
            ],
            [
                'NO',
                'date',
                (self.dt + timedelta(days=5)).date().strftime('%Y-%m-%d'),
                '$444.44',
                'ST4',
                'BankOne (1)',
                'Periodic1 (1)'
            ]
        ]
        linkcols = [
            [
                c[4].get_attribute('innerHTML'),
                c[5].get_attribute('innerHTML'),
                c[6].get_attribute('innerHTML')
            ]
            for c in elems
        ]
        assert linkcols[0] == [
            '<a href="javascript:schedModal(3)">ST3</a>',
            '<a href="/accounts/2">BankTwoStale (2)</a>',
            '<a href="/budgets/4">Standing1 (4)</a>'
        ]
        assert linkcols[1] == [
            '<a href="javascript:schedModal(2)">ST2</a>',
            '<a href="/accounts/1">BankOne (1)</a>',
            '<a href="/budgets/2">Periodic2 (2)</a>'
        ]
        assert linkcols[2] == [
            '<a href="javascript:schedModal(1)">ST1</a>',
            '<a href="/accounts/1">BankOne (1)</a>',
            '<a href="/budgets/1">Periodic1 (1)</a>'
        ]
        assert linkcols[3] == [
            '<a href="javascript:schedModal(6)">ST6</a>',
            '<a href="/accounts/2">BankTwoStale (2)</a>',
            '<a href="/budgets/4">Standing1 (4)</a>'
        ]
        assert linkcols[4] == [
            '<a href="javascript:schedModal(5)">ST5</a>',
            '<a href="/accounts/1">BankOne (1)</a>',
            '<a href="/budgets/2">Periodic2 (2)</a>'
        ]
        assert linkcols[5] == [
            '<a href="javascript:schedModal(4)">ST4</a>',
            '<a href="/accounts/1">BankOne (1)</a>',
            '<a href="/budgets/1">Periodic1 (1)</a>'
        ]

    def test_filter_opts(self, selenium):
        selenium.get(self.baseurl + '/scheduled')
        acct_filter = Select(selenium.find_element_by_id('type_filter'))
        # find the options
        opts = []
        for o in acct_filter.options:
            opts.append([o.get_attribute('value'), o.text])
        assert opts == [
            ['None', ''],
            ['date', 'Date'],
            ['monthly', 'Monthly'],
            ['per period', 'Per Period']
        ]

    def test_filter(self, selenium):
        p1trans = [
            'ST3',
            'ST2',
            'ST1',
            'ST6',
            'ST5',
            'ST4'
        ]
        selenium.get(self.baseurl + '/scheduled')
        table = self.retry_stale(
            selenium.find_element_by_id,
            'table-scheduled-txn'
        )
        texts = self.retry_stale(self.tbody2textlist, table)
        trans = [t[4] for t in texts]
        # check sanity
        assert trans == p1trans
        type_filter = Select(selenium.find_element_by_id('type_filter'))
        # select Monthly
        type_filter.select_by_value('monthly')
        table = self.retry_stale(
            selenium.find_element_by_id,
            'table-scheduled-txn'
        )
        texts = self.retry_stale(self.tbody2textlist, table)
        trans = [t[4] for t in texts]
        assert trans == ['ST2', 'ST5']
        # select back to all
        type_filter.select_by_value('None')
        table = self.retry_stale(
            selenium.find_element_by_id,
            'table-scheduled-txn'
        )
        texts = self.retry_stale(self.tbody2textlist, table)
        trans = [t[4] for t in texts]
        assert trans == p1trans

    def test_search(self, selenium):
        selenium.get(self.baseurl + '/scheduled')
        search = self.retry_stale(
            selenium.find_element_by_xpath,
            '//input[@type="search"]'
        )
        search.send_keys('ST3')
        table = self.retry_stale(
            selenium.find_element_by_id,
            'table-scheduled-txn'
        )
        texts = self.retry_stale(self.tbody2textlist, table)
        trans = [t[4] for t in texts]
        # check sanity
        assert trans == ['ST3']


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestSchedTransModalPerPeriod(AcceptanceHelper):

    def test_0_verify_db(self, testdb):
        t = testdb.query(ScheduledTransaction).get(3)
        assert t.description == 'ST3'
        assert t.num_per_period == 1
        assert t.date is None
        assert t.day_of_month is None
        assert float(t.amount) == -333.33
        assert t.account_id == 2
        assert t.budget_id == 4
        assert t.notes == 'notesST3'
        assert t.is_active is True

    def test_1_modal_on_click(self, base_url, selenium):
        self.baseurl = base_url
        selenium.get(base_url + '/scheduled')
        link = selenium.find_element_by_xpath('//a[text()="ST3"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Scheduled Transaction 3'
        assert body.find_element_by_id(
            'sched_frm_id').get_attribute('value') == '3'
        assert body.find_element_by_id(
            'sched_frm_description').get_attribute('value') == 'ST3'
        assert body.find_element_by_id(
            'sched_frm_type_monthly').is_selected() is False
        assert body.find_element_by_id(
            'sched_frm_type_date').is_selected() is False
        assert body.find_element_by_id(
            'sched_frm_type_per_period').is_selected()
        assert body.find_element_by_id(
            'sched_frm_num_per_period').get_attribute('value') == '1'
        assert body.find_element_by_id(
            'sched_frm_amount').get_attribute('value') == '-333.33'
        acct_sel = Select(body.find_element_by_id('sched_frm_account'))
        opts = []
        for o in acct_sel.options:
            opts.append([o.get_attribute('value'), o.text])
        assert opts == [
            ['None', ''],
            ['1', 'BankOne'],
            ['2', 'BankTwoStale'],
            ['3', 'CreditOne'],
            ['4', 'CreditTwo'],
            ['6', 'DisabledBank'],
            ['5', 'InvestmentOne']
        ]
        assert acct_sel.first_selected_option.get_attribute('value') == '2'
        budget_sel = Select(body.find_element_by_id('sched_frm_budget'))
        opts = []
        for o in budget_sel.options:
            opts.append([o.get_attribute('value'), o.text])
        assert opts == [
            ['None', ''],
            ['1', 'Periodic1'],
            ['2', 'Periodic2'],
            ['3', 'Periodic3 Inactive'],
            ['4', 'Standing1'],
            ['5', 'Standing2'],
            ['6', 'Standing3 Inactive']
        ]
        assert budget_sel.first_selected_option.get_attribute('value') == '4'
        assert selenium.find_element_by_id('sched_frm_active').is_selected()

    def test_2_modal_edit(self, base_url, selenium):
        pass

    def test_3_verify_db(self, testdb):
        pass


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestSchedTransMonthlyURL(AcceptanceHelper):

    def test_0_verify_db(self, testdb):
        t = testdb.query(ScheduledTransaction).get(2)
        assert t.description == 'ST2'
        assert t.num_per_period is None
        assert t.date is None
        assert t.day_of_month == 4
        assert float(t.amount) == 222.22
        assert t.account_id == 1
        assert t.budget_id == 2
        assert t.notes == 'notesST2'
        assert t.is_active is True

    def test_1_modal_from_url(self, base_url, selenium):
        self.baseurl = base_url
        selenium.get(base_url + '/scheduled/2')
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Scheduled Transaction 2'
        assert body.find_element_by_id(
            'sched_frm_id').get_attribute('value') == '2'
        assert body.find_element_by_id(
            'sched_frm_description').get_attribute('value') == 'ST2'
        assert body.find_element_by_id(
            'sched_frm_type_monthly').is_selected()
        assert body.find_element_by_id(
            'sched_frm_type_date').is_selected() is False
        assert body.find_element_by_id(
            'sched_frm_type_per_period').is_selected() is False
        assert body.find_element_by_id(
            'sched_frm_day_of_month').get_attribute('value') == '4'
        assert body.find_element_by_id(
            'sched_frm_amount').get_attribute('value') == '222.22'
        acct_sel = Select(body.find_element_by_id('sched_frm_account'))
        assert acct_sel.first_selected_option.get_attribute('value') == '1'
        budget_sel = Select(body.find_element_by_id('sched_frm_budget'))
        assert budget_sel.first_selected_option.get_attribute('value') == '2'
        assert selenium.find_element_by_id('sched_frm_active').is_selected()

    def test_2_modal_edit(self, base_url, selenium):
        pass

    def test_3_verify_db(self, testdb):
        pass


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestSchedTransDateInactive(AcceptanceHelper):

    def test_0_verify_db(self, testdb):
        t = testdb.query(ScheduledTransaction).get(4)
        assert t.description == 'ST4'
        assert t.num_per_period is None
        assert t.date == (
            dtnow() + timedelta(days=5)
        ).date()
        assert t.day_of_month is None
        assert float(t.amount) == 444.44
        assert t.account_id == 1
        assert t.budget_id == 1
        assert t.notes == 'notesST4'
        assert t.is_active is False

    def test_1_modal_from_url(self, base_url, selenium):
        self.baseurl = base_url
        selenium.get(base_url + '/scheduled/4')
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Scheduled Transaction 4'
        assert body.find_element_by_id(
            'sched_frm_id').get_attribute('value') == '4'
        assert body.find_element_by_id(
            'sched_frm_description').get_attribute('value') == 'ST4'
        assert body.find_element_by_id(
            'sched_frm_type_monthly').is_selected() is False
        assert body.find_element_by_id(
            'sched_frm_type_date').is_selected()
        assert body.find_element_by_id(
            'sched_frm_type_per_period').is_selected() is False
        assert body.find_element_by_id(
            'sched_frm_date').get_attribute('value') == (
            dtnow() + timedelta(days=5)).strftime('%Y-%m-%d')
        assert body.find_element_by_id(
            'sched_frm_amount').get_attribute('value') == '444.44'
        acct_sel = Select(body.find_element_by_id('sched_frm_account'))
        assert acct_sel.first_selected_option.get_attribute('value') == '1'
        budget_sel = Select(body.find_element_by_id('sched_frm_budget'))
        assert budget_sel.first_selected_option.get_attribute('value') == '1'
        assert selenium.find_element_by_id(
            'sched_frm_active').is_selected() is False

    def test_2_modal_edit(self, base_url, selenium):
        pass

    def test_3_verify_db(self, testdb):
        pass