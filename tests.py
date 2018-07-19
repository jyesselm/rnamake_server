from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

import argparse
import unittest
import os
import pandas as pd
from rnamake_server import job_queue, daemon, settings


def get_job_id_from_url(url):
    spl = url.split("/")
    return spl[4]

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

def get_scaffold_args(
        pdb_file="res/unittest_res/test_pdbs/test_scaffold/min_tetraloop_receptor.pdb",
        nstruct ="1",
        start_bp="A221-A252",
        end_bp  ="A145-A158",
        email   = ""):

    pdb_file = os.path.abspath(pdb_file)
    return locals()

def test_case(page, driver, args):
    driver.get(page)
    for n, v in args.iteritems():
        driver.find_element_by_id(n).send_keys(v)
    driver.find_element_by_id("submit_button").click()


def failed_to_submit(page, driver, args):
    test_case(page, driver, args)
    alert_text = get_alert_text(driver)
    if len(alert_text) > 0:
        driver.switch_to.alert.accept()
    if url_changed(page, driver):
        return False
    else:
        return True

######################################################################################
# ACTUAL TESTS

class WebserverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.design_scaffold_app_url = "http://127.0.0.1:8080/design_scaffold_app"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    ### tests
    def test_missing_elements_for_scaffold(self):
        removed_args = "pdb_file nstruct start_bp end_bp".split()

        for a in removed_args:
            args = get_scaffold_args()
            args[a] = ""

            failed = failed_to_submit(self.design_scaffold_app_url, self.driver, args)
            if not failed:
                self.fail("did not fail when it should of, " + a + " was nor filled in but yet ")



def test_missing_elements(page, driver):
    removed_args = "pdb_file nstruct start_bp end_bp".split()

    for a in removed_args:
        args = get_scaffold_args()
        args[a] = ""

        failed = failed_to_submit(page, driver, args)
        if not failed:
            print "did not fail when it should of, " + a + " was nor filled in but yet "

def test_improper_arguments(page, driver):
    # test not a pdb file
    args = get_scaffold_args(pdb_file="res/unittest_res/NOT_A_PDB")
    if not failed_to_submit(page, driver, args):
        print "accepted a invalid pdb!!"

    # residue doesnt exist
    args = get_scaffold_args(start_bp="A1-A252")
    if not failed_to_submit(page, driver, args):
        print "accepted a basepair with an invalid residue"

    # bp does not exist
    args = get_scaffold_args(start_bp="A222-A252")
    if not failed_to_submit(page, driver, args):
        print "accepted an invalid basepair"

    # bp is not a end bp
    args = get_scaffold_args(start_bp="A222-A251")
    if not failed_to_submit(page, driver, args):
        print "accepted a basepair that is not an end"

def test_submitting_a_job(page, driver, jq):
    args = get_scaffold_args()
    if failed_to_submit(page, driver, args):
        print "should of submitted"

    j_id = get_job_id_from_url(driver.current_url)
    jq.delete_job(j_id)

def test_full_job(page, driver, jq, d, args=None):
    if args is None:
        args = get_scaffold_args()
    if failed_to_submit(page, driver, args):
        print "should of submitted"

    j_id = get_job_id_from_url(driver.current_url)
    d.run_job(j_id)
    driver.get(driver.current_url)

    try:
        row = driver.find_element_by_id("result_row_0")
        html = row.get_attribute('innerHTML')
        if len(html) < 1000:
            print "found result element but it is too short probably wrong"
    except NoSuchElementException:
        print "could not successfully find results"

    jq.delete_job(j_id)

def test_length_striction(driver, jq, d):
    #vs_ribozyme.pdb, A625 - A635, A727 - A748
    pass

def run_all_scaffold_tests(driver, jq, d):
    path = settings.RES_DIR + "/unittest_res/design_rna_tests.txt"
    df = pd.read_csv(path)

    pdb_path = "res/unittest_res/test_pdbs/test_scaffold/"
    for i, r in df.iterrows():
        args = get_scaffold_args(pdb_file=pdb_path+r.pdb,
                                 start_bp=r.start_bp,
                                 end_bp=r.end_bp)

        test_full_job(design_scaffold_app_url, driver, jq, d, args)
        driver.get_screenshot_as_file(settings.TOP_DIR + "/tests/screenshots/"+r.pdb[:-4]+".png")


if __name__ == "__main__":
    unittest.main()


    exit()
    design_scaffold_app_url = "http://127.0.0.1:8080/design_scaffold_app"

    # Using Chrome to access web
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    #driver = webdriver.Chrome(chrome_options=chrome_options)
    driver = webdriver.Chrome()
    driver.get(design_scaffold_app_url)

    # make sure requires all critical arguments
    #test_missing_elements(design_scaffold_app_url, driver)

    # improper form values
    #test_improper_arguments(design_scaffold_app_url, driver)

    jq = job_queue.JobQueue()
    #test_submitting_a_job(design_scaffold_app_url, driver, jq)

    d = daemon.RNAMakeDaemon("devel")
    #test_full_job(design_scaffold_app_url, driver, jq, d)

    # all job tests
    run_all_scaffold_tests(driver, jq, d)


    driver.quit()


"""path = "/Users/jyesselm/projects/RNAMake.projects/rnamake_server/test_pdbs/test_scaffold/min_tetraloop_receptor.pdb"
driver.find_element_by_id("pdb_file").send_keys(path)
driver.find_element_by_id("nstruct").send_keys("1")
driver.find_element_by_id("start_bp").send_keys("A221-A252")
driver.find_element_by_id("end_bp").send_keys("A145-A158")
driver.find_element_by_id("submit_button").click()




print driver.current_url

driver.quit()

#driver.find_element_by_id("scaffold_button").click()"""
