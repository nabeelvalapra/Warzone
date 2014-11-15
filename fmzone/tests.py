from django.test import TestCase
from fmzone.models import Persons
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Create your tests here.
class PersonTest(TestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_via_admin_site(self):
        # Gertrude opens her web browser, and goes to the admin page
        self.browser.get( 'localhost:8000/admin/')

        # She sees the familiar 'Django administration' heading
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Django administration', body.text)
        
        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('nabeel')

        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('nabeel')
        password_field.send_keys(Keys.RETURN)

        # her username and password are accepted, and she is taken to
        # the Site Administration page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)

        # She now sees a couple of hyperlink that says "Polls"
        polls_links = self.browser.find_elements_by_link_text('Polls')
        self.assertEquals(len(polls_links), 2)


        # TODO: use the admin site to create a Poll
        # self.fail('finish this test')
        #     self.