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
from sqlalchemy import func
from time import sleep
from biweeklybudget.models.projects import Project, BoMItem
from biweeklybudget.tests.acceptance_helpers import AcceptanceHelper


@pytest.mark.acceptance
class TestProjects(AcceptanceHelper):

    @pytest.fixture(autouse=True)
    def get_page(self, base_url, selenium, testflask, refreshdb):  # noqa
        self.baseurl = base_url
        self.get(selenium, base_url + '/projects')

    def test_heading(self, selenium):
        heading = selenium.find_element_by_class_name('navbar-brand')
        assert heading.text == 'Projects / Bill of Materials - BiweeklyBudget'

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
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb', 'testflask')
class TestProjectsView(AcceptanceHelper):

    def test_00_verify_db(self, testdb):
        b = testdb.query(Project).get(1)
        assert b is not None
        assert b.name == 'P1'
        assert b.notes == 'ProjectOne'
        assert b.is_active is True
        b = testdb.query(Project).get(2)
        assert b is not None
        assert b.name == 'P2'
        assert b.notes == 'ProjectTwo'
        assert b.is_active is True
        b = testdb.query(Project).get(3)
        assert b is not None
        assert b.name == 'P3Inactive'
        assert b.notes == 'ProjectThreeInactive'
        assert b.is_active is False
        assert testdb.query(Project).with_entities(
            func.max(Project.id)
        ).scalar() == 3
        assert testdb.query(BoMItem).with_entities(
            func.max(BoMItem.id)
        ).scalar() == 5

    def test_01_table(self, base_url, selenium):
        self.get(selenium, base_url + '/projects')
        table = selenium.find_element_by_id('table-projects')
        htmls = self.inner_htmls(self.tbody2elemlist(table))
        assert htmls == [
            [
                '<a href="/projects/1">P1</a>',
                '$2,546.89',
                '$77.77',
                'yes <a onclick="deactivateProject(1);" href="#">'
                '(deactivate)</a>',
                'ProjectOne'
            ],
            [
                '<a href="/projects/2">P2</a>',
                '$0',
                '$0',
                'yes <a onclick="deactivateProject(2);" href="#">'
                '(deactivate)</a>',
                'ProjectTwo'
            ],
            [
                '<a href="/projects/3">P3Inactive</a>',
                '$5.34',
                '$3',
                'NO <a onclick="activateProject(3);" href="#">'
                '(activate)</a>',
                'ProjectThreeInactive'
            ]
        ]

    def test_02_search(self, base_url, selenium):
        self.get(selenium, base_url + '/projects')
        search = self.retry_stale(
            selenium.find_element_by_xpath,
            '//input[@type="search"]'
        )
        search.send_keys('Inact')
        sleep(1)
        self.wait_for_jquery_done(selenium)
        table = self.retry_stale(
            selenium.find_element_by_id,
            'table-projects'
        )
        htmls = self.inner_htmls(self.tbody2elemlist(table))
        assert htmls == [
            [
                '<a href="/projects/3">P3Inactive</a>',
                '$5.34',
                '$3',
                'NO <a onclick="activateProject(3);" href="#">(activate)</a>',
                'ProjectThreeInactive'
            ]
        ]

    def test_03_add(self, base_url, selenium):
        self.get(selenium, base_url + '/projects')
        name = selenium.find_element_by_id('proj_frm_name')
        name.clear()
        name.send_keys('NewP')
        notes = selenium.find_element_by_id('proj_frm_notes')
        notes.clear()
        notes.send_keys('My New Project')
        btn = selenium.find_element_by_id('formSaveButton')
        btn.click()
        self.wait_for_jquery_done(selenium)
        table = self.retry_stale(
            selenium.find_element_by_id,
            'table-projects'
        )
        htmls = self.inner_htmls(self.tbody2elemlist(table))
        assert htmls == [
            [
                '<a href="/projects/4">NewP</a>',
                '$0',
                '$0',
                'yes <a onclick="deactivateProject(4);" href="#">'
                '(deactivate)</a>',
                'My New Project'
            ],
            [
                '<a href="/projects/1">P1</a>',
                '$2,546.89',
                '$77.77',
                'yes <a onclick="deactivateProject(1);" href="#">'
                '(deactivate)</a>',
                'ProjectOne'
            ],
            [
                '<a href="/projects/2">P2</a>',
                '$0',
                '$0',
                'yes <a onclick="deactivateProject(2);" href="#">'
                '(deactivate)</a>',
                'ProjectTwo'
            ],
            [
                '<a href="/projects/3">P3Inactive</a>',
                '$5.34',
                '$3',
                'NO <a onclick="activateProject(3);" href="#">'
                '(activate)</a>',
                'ProjectThreeInactive'
            ]
        ]

    def test_04_verify_db(self, testdb):
        b = testdb.query(Project).get(1)
        assert b is not None
        assert b.name == 'P1'
        assert b.notes == 'ProjectOne'
        assert b.is_active is True
        b = testdb.query(Project).get(2)
        assert b is not None
        assert b.name == 'P2'
        assert b.notes == 'ProjectTwo'
        assert b.is_active is True
        b = testdb.query(Project).get(3)
        assert b is not None
        assert b.name == 'P3Inactive'
        assert b.notes == 'ProjectThreeInactive'
        assert b.is_active is False
        b = testdb.query(Project).get(4)
        assert b is not None
        assert b.name == 'NewP'
        assert b.notes == 'My New Project'
        assert b.is_active is True
        assert testdb.query(Project).with_entities(
            func.max(Project.id)
        ).scalar() == 4
        assert testdb.query(BoMItem).with_entities(
            func.max(BoMItem.id)
        ).scalar() == 5

    def test_05_deactivate(self, base_url, selenium):
        self.get(selenium, base_url + '/projects')
        link = selenium.find_element_by_xpath(
            '//a[@onclick="deactivateProject(1);"]'
        )
        link.click()
        self.wait_for_jquery_done(selenium)
        table = self.retry_stale(
            selenium.find_element_by_id,
            'table-projects'
        )
        htmls = self.inner_htmls(self.tbody2elemlist(table))
        assert htmls == [
            [
                '<a href="/projects/4">NewP</a>',
                '$0',
                '$0',
                'yes <a onclick="deactivateProject(4);" href="#">'
                '(deactivate)</a>',
                'My New Project'
            ],
            [
                '<a href="/projects/2">P2</a>',
                '$0',
                '$0',
                'yes <a onclick="deactivateProject(2);" href="#">'
                '(deactivate)</a>',
                'ProjectTwo'
            ],
            [
                '<a href="/projects/1">P1</a>',
                '$2,546.89',
                '$77.77',
                'NO <a onclick="activateProject(1);" href="#">'
                '(activate)</a>',
                'ProjectOne'
            ],
            [
                '<a href="/projects/3">P3Inactive</a>',
                '$5.34',
                '$3',
                'NO <a onclick="activateProject(3);" href="#">'
                '(activate)</a>',
                'ProjectThreeInactive'
            ]
        ]

    def test_06_verify_db(self, testdb):
        b = testdb.query(Project).get(1)
        assert b is not None
        assert b.name == 'P1'
        assert b.notes == 'ProjectOne'
        assert b.is_active is False
        b = testdb.query(Project).get(2)
        assert b is not None
        assert b.name == 'P2'
        assert b.notes == 'ProjectTwo'
        assert b.is_active is True
        b = testdb.query(Project).get(3)
        assert b is not None
        assert b.name == 'P3Inactive'
        assert b.notes == 'ProjectThreeInactive'
        assert b.is_active is False
        b = testdb.query(Project).get(4)
        assert b is not None
        assert b.name == 'NewP'
        assert b.notes == 'My New Project'
        assert b.is_active is True
        assert testdb.query(Project).with_entities(
            func.max(Project.id)
        ).scalar() == 4
        assert testdb.query(BoMItem).with_entities(
            func.max(BoMItem.id)
        ).scalar() == 5

    def test_07_activate(self, base_url, selenium):
        self.get(selenium, base_url + '/projects')
        link = selenium.find_element_by_xpath(
            '//a[@onclick="activateProject(3);"]'
        )
        link.click()
        self.wait_for_jquery_done(selenium)
        table = self.retry_stale(
            selenium.find_element_by_id,
            'table-projects'
        )
        htmls = self.inner_htmls(self.tbody2elemlist(table))
        assert htmls == [
            [
                '<a href="/projects/4">NewP</a>',
                '$0',
                '$0',
                'yes <a onclick="deactivateProject(4);" href="#">'
                '(deactivate)</a>',
                'My New Project'
            ],
            [
                '<a href="/projects/2">P2</a>',
                '$0',
                '$0',
                'yes <a onclick="deactivateProject(2);" href="#">'
                '(deactivate)</a>',
                'ProjectTwo'
            ],
            [
                '<a href="/projects/3">P3Inactive</a>',
                '$5.34',
                '$3',
                'yes <a onclick="deactivateProject(3);" href="#">'
                '(deactivate)</a>',
                'ProjectThreeInactive'
            ],
            [
                '<a href="/projects/1">P1</a>',
                '$2,546.89',
                '$77.77',
                'NO <a onclick="activateProject(1);" href="#">'
                '(activate)</a>',
                'ProjectOne'
            ]
        ]

    def test_08_verify_db(self, testdb):
        b = testdb.query(Project).get(1)
        assert b is not None
        assert b.name == 'P1'
        assert b.notes == 'ProjectOne'
        assert b.is_active is False
        b = testdb.query(Project).get(2)
        assert b is not None
        assert b.name == 'P2'
        assert b.notes == 'ProjectTwo'
        assert b.is_active is True
        b = testdb.query(Project).get(3)
        assert b is not None
        assert b.name == 'P3Inactive'
        assert b.notes == 'ProjectThreeInactive'
        assert b.is_active is True
        b = testdb.query(Project).get(4)
        assert b is not None
        assert b.name == 'NewP'
        assert b.notes == 'My New Project'
        assert b.is_active is True
        assert testdb.query(Project).with_entities(
            func.max(Project.id)
        ).scalar() == 4
        assert testdb.query(BoMItem).with_entities(
            func.max(BoMItem.id)
        ).scalar() == 5
