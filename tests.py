from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
import os
from rnamake_server import job_queue


def get_alert_text(driver):
    try:
        return driver.switch_to.alert.text
    except NoAlertPresentException:
        return ""


def url_changed(expected, driver):
    if expected != driver.current_url:
        return True
    else:
        return False

def get_args(
        pdb_file="test_pdbs/test_scafold/min_tetraloop_receptor.pdb",
        nstruct ="1",
        start_bp="A221-A252",
        end_bp  ="A145-A158",
        email   = ""):

    pdb_file = os.path.abspath(pdb_file)
    return locals()

def test_case(driver, args):
    for n, v in args.iteritems():
        driver.find_element_by_id(n).send_keys(v)
    driver.find_element_by_id("submit_button").click()

######################################################################################
# ACTUAL TESTS

def test_missing_elements(driver):
    pass



if __name__ == "__main__":
    pass


design_scaffold_app_url = "http://127.0.0.1:8080/design_scaffold_app"


# Using Chrome to access web
driver = webdriver.Chrome()
driver.get(design_scaffold_app_url)

args = get_args()
args["pdb_file"] = ""
test_case(driver, args)
print url_changed(design_scaffold_app_url, driver)
driver.quit()

exit()


path = "/Users/jyesselm/projects/RNAMake.projects/rnamake_server/test_pdbs/test_scaffold/min_tetraloop_receptor.pdb"
driver.find_element_by_id("pdb_file").send_keys(path)
driver.find_element_by_id("nstruct").send_keys("1")
driver.find_element_by_id("start_bp").send_keys("A221-A252")
driver.find_element_by_id("end_bp").send_keys("A145-A158")
driver.find_element_by_id("submit_button").click()




print driver.current_url

driver.quit()

#driver.find_element_by_id("scaffold_button").click()
