import unittest, sys, time
sys.path.extend(['.','..','../..','py'])
import h2o, h2o_hosts, h2o_cmd, h2o_import as h2i, h2o_common, h2o_print, h2o_rf


# RF train parameters
paramsTrainRF = { 
    'ntree'      : 50, 
    'depth'      : 30,
    'parallel'   : 1, 
    'bin_limit'  : 10000,
    'ignore'     : 'AirTime, ArrDelay, DepDelay, CarrierDelay, IsArrDelayed', 
    'stat_type'  : 'ENTROPY',
    'out_of_bag_error_estimate': 1, 
    'exclusive_split_limit'    : 0,
    'timeoutSecs': 14800,
    'iterative_cm': 0,
    }

# RF test parameters
paramsScoreRF = {
    # scoring requires the response_variable. it defaults to last, so normally
    # we don't need to specify. But put this here and (above if used) 
    # in case a dataset doesn't use last col 
    'response_variable': None,
    'out_of_bag_error_estimate': 0, 
    'timeoutSecs': 14800,
    }

trainDS = {
    'csvFilename' : 'airlines_all.csv',
    'timeoutSecs' : 14800,
    'header'      : 1
    }

# FIX should point to a different smaller dataset
scoreDS = {
    'csvFilename' : 'airlines_all.csv',
    'timeoutSecs' : 14800,
    'header'      : 1
    }

PARSE_TIMEOUT=14800


class releaseTest(h2o_common.ReleaseCommon, unittest.TestCase):

    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        h2o_hosts.build_cloud_with_hosts()
        
    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()
        
    def parseFile(self, importFolderPath='datasets', csvFilename='airlines_all.csv', **kwargs):
        csvPathname = importFolderPath + "/" + csvFilename

        # FIX! does 'separator=' take ints or ?? hex format
        # looks like it takes the hex string (two chars)
        start = time.time()
        # hardwire TAB as a separator, as opposed to white space (9)
        parseResult = h2i.import_parse(path=csvPathname, schema='hdfs', timeoutSecs=500, separator=9)
        elapsed = time.time() - start
        print "Parse of", parseResult['destination_key'], "took", elapsed, "seconds"
        parseResult['python_call_timer'] = elapsed
        print "Parse result['destination_key']:", parseResult['destination_key']

        start = time.time()
        inspect = h2o_cmd.runInspect(None, parseResult['destination_key'], timeoutSecs=500)
        print "Inspect:", parseResult['destination_key'], "took", time.time() - start, "seconds"
        h2o_cmd.infoFromInspect(inspect, csvPathname)
        num_rows = inspect['num_rows']
        num_cols = inspect['num_cols']
        print "num_rows:", num_rows, "num_cols", num_cols

    def loadTrainData(self):
        kwargs   = trainDS.copy()
        trainKey = self.parseFile(**kwargs)
        return trainKey
    
    def loadScoreData(self):
        kwargs   = scoreDS.copy()
        scoreKey = self.parseFile(**kwargs)
        return scoreKey 

    def test_c8_rf_airlines_hdfs(self):
        trainKey = self.loadTrainData()
        kwargs   = paramsTrainRF.copy()
        trainResult = h2o_rf.trainRF(trainKey, **kwargs)

        scoreKey = self.loadScoreData()
        kwargs   = paramsScoreRF.copy()
        scoreResult = h2o_rf.scoreRF(scoreKey, trainResult, **kwargs)

        print "\nTrain\n=========={0}".format(h2o_rf.pp_rf_result(trainResult))
        print "\nScoring\n========={0}".format(h2o_rf.pp_rf_result(scoreResult))

if __name__ == '__main__':
    h2o.unit_main()
