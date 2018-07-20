from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

import sys
import argparse
import unittest
import os
import pandas as pd
from rnamake_server import job_queue, daemon, settings


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', help='address', default="127.0.0.1:8080")
    parser.add_argument('unittest_args', nargs='*')
    args = parser.parse_args()
    return args

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

def get_stablization_args(
        pdb_file="res/unittest_res/test_pdbs/test_scaffold/min_tetraloop_receptor.pdb",
        nstruct="1",
        email=""):
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


def run_full_job(page, driver, jq, d, args=None, delete_job=True):
    if args is None:
        args = get_scaffold_args()
    if failed_to_submit(page, driver, args):
        return "should of submitted"

    j_id = get_job_id_from_url(driver.current_url)
    d.run_job(j_id)
    driver.get(driver.current_url)

    try:
        row = driver.find_element_by_id("result_row_0")
        html = row.get_attribute('innerHTML')
        if len(html) < 500:
            return "found result element but it is too short probably wrong"
    except NoSuchElementException:
        return "could not successfully find results"

    if delete_job:
        jq.delete_job(j_id)
    return None

######################################################################################
# ACTUAL TESTS

class DesignScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.page = "http://127.0.0.1:8080/design_scaffold_app"
        cls.jq = job_queue.JobQueue()
        cls.daemon = daemon.RNAMakeDaemon("devel")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    ### tests
    def test_missing_elements(self):
        removed_args = "pdb_file nstruct start_bp end_bp".split()

        for a in removed_args:
            args = get_scaffold_args()
            args[a] = ""

            failed = failed_to_submit(self.page, self.driver, args)
            if not failed:
                self.fail("did not fail when it should of, " + a + " was nor filled in but yet ")

    def test_improper_arguments(self):
        # test not a pdb file
        args = get_scaffold_args(pdb_file="res/unittest_res/NOT_A_PDB")
        if not failed_to_submit(self.page, self.driver, args):
            self.fail("accepted a invalid pdb!! " + str(args))

        # residue doesnt exist
        args = get_scaffold_args(start_bp="A1-A252")
        if not failed_to_submit(self.page, self.driver, args):
            self.fail("accepted a basepair with an invalid residue" + str(args))

        # bp does not exist
        args = get_scaffold_args(start_bp="A222-A252")
        if not failed_to_submit(self.page, self.driver, args):
            self.fail("accepted an invalid basepair" + str(args))

        # bp is not a end bp
        args = get_scaffold_args(start_bp="A222-A251")
        if not failed_to_submit(self.page, self.driver, args):
            self.fail("accepted a basepair that is not an end" + str(args))

        # pdb is too big > 100 residues
        pdb_path = "res/unittest_res/test_pdbs/test_scaffold/vs_ribozyme.pdb"
        args = get_scaffold_args(pdb_file=pdb_path,start_bp="A625-A635",end_bp="A727-A748")
        if not failed_to_submit(self.page, self.driver, args):
            self.fail("accepted a pdb that is too big" + str(args))

    def test_submitting_a_job(self):
        args = get_scaffold_args()
        if failed_to_submit(self.page, self.driver, args):
            self.fail("should of submitted")

        j_id = get_job_id_from_url(self.driver.current_url)
        self.jq.delete_job(j_id)

    def test_run_full_job(self):
        error = run_full_job(self.page, self.driver, self.jq, self.daemon)
        if error is not None:
            self.fail(error)

    def test_run_scaffolding_problems(self):
        path = settings.RES_DIR + "/unittest_res/design_rna_tests.txt"
        df = pd.read_csv(path)

        pdb_path = "res/unittest_res/test_pdbs/test_scaffold/"
        for i, r in df.iterrows():
            args = get_scaffold_args(pdb_file=pdb_path + r.pdb,
                                     start_bp=r.start_bp,
                                     end_bp=r.end_bp)

            error = run_full_job(self.page, self.driver, self.jq, self.daemon, args)
            if error is not None:
                self.fail(error)
            #driver.get_screenshot_as_file(settings.TOP_DIR + "/tests/screenshots/"+r.pdb[:-4]+".png")

    # dont spam me!
    def _test_email(self):
        args = get_scaffold_args(email="jyesselm@stanford.edu")
        error = run_full_job(self.page, self.driver, self.jq, self.daemon, args, delete_job=False)
        if error is not None:
            self.fail(error)


class AptStablizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.page = "http://"+g_args.a+"/apt_stablization_app"
        cls.jq = job_queue.JobQueue()
        cls.daemon = daemon.RNAMakeDaemon("devel")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    ### tests
    def test_missing_elements(self):
        removed_args = "pdb_file nstruct".split()

        for a in removed_args:
            args = get_stablization_args()
            args[a] = ""

            failed = failed_to_submit(self.page, self.driver, args)
            if not failed:
                self.fail(
                    "did not fail when it should of, " + a + " was nor filled in but yet ")

    def test_improper_arguments(self):
        # test not a pdb file
        args = get_stablization_args(pdb_file="res/unittest_res/NOT_A_PDB")
        if not failed_to_submit(self.page, self.driver, args):
            self.fail("accepted a invalid pdb!! " + str(args))

    def test_submitting_a_job(self):
        args = get_stablization_args()
        if failed_to_submit(self.page, self.driver, args):
            self.fail("should of submitted")

        j_id = get_job_id_from_url(self.driver.current_url)
        self.jq.delete_job(j_id)

    def test_run_full_job(self):
        error = run_full_job(self.page, self.driver, self.jq, self.daemon)
        if error is not None:
            self.fail(error)


if __name__ == "__main__":
    g_args = parse_args()
    sys.argv[1:] = g_args.unittest_args
    unittest.main()



