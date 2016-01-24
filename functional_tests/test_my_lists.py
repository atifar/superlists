import time
from django.conf import settings
from .base import FunctionalTest, TEST_EMAIL
from .server_tools import create_session_on_server
from .management.commands.create_session import (
    create_pre_authenticated_session
)


class MyListsTest(FunctionalTest):

    def create_pre_authenticated_session(self, email):
        if self.against_staging:
            session_key = create_session_on_server(
                self.server_host,
                email
            )
        else:
            session_key = create_pre_authenticated_session(email)
        ## to set a cookie we need to first visit the domain.
        ## 404 pages load the quickest!
        self.browser.get(self.server_url + "/404_no_such_url/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/',
        ))

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        # email = 'edith@example.com'
        #
        # # Edith is a Logged-in user
        # self.create_pre_authenticated_session(email)

        # Edith goes to the awesome superlists site
        # and notices a "Sign in" link for the first time.
        self.browser.get(self.server_url)
        self.browser.find_element_by_id('id_login').click()

        # A Persona login box appears
        self.switch_to_new_window('Mozilla Persona')

        # Edith logs in with her email address
        self.browser.find_element_by_id(
            'authentication_email'
        ).send_keys(TEST_EMAIL)
        self.browser.find_element_by_tag_name('button').click()

        # The Persona window closes
        self.switch_to_new_window('To-Do')

        time.sleep(1)
        # She can see that she is logged in
        self.wait_to_be_logged_in(email=TEST_EMAIL)

        # She goes to the home page and starts a list
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('Reticulate splines\n')
        self.get_item_input_box().send_keys('Immanentize eschaton\n')
        time.sleep(1)
        first_list_url = self.browser.current_url

        # She notices a "My lists" link, for the first time
        self.browser.find_element_by_link_text('My lists').click()
        time.sleep(1)
        self.wait_for_element_with_id('id_owners_list')

        # She sees that her list is in there, named according to its
        # first list item
        self.browser.find_element_by_link_text('Reticulate splines').click()
        time.sleep(1)
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )
        # She decides to start another list, just to see
        self.browser.get(self.server_url)
        self.get_item_input_box().send_keys('Click cows\n')
        time.sleep(6)
        second_list_url = self.browser.current_url

        # Under "My lists", her new list appears
        self.browser.find_element_by_link_text('My lists').click()
        time.sleep(1)
        self.wait_for_element_with_id('id_owners_list')
        self.browser.find_element_by_link_text('Click cows').click()
        time.sleep(1)
        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, second_list_url)
        )

        # She logs out. The "My lists" option disappears
        self.browser.find_element_by_id('id_logout').click()
        time.sleep(5)
        self.assertEqual(
            self.browser.find_elements_by_link_text('My lists'),
            []
        )
