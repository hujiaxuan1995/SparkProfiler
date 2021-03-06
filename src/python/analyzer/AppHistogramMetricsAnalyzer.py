import os
import statistics.HistogramStatistics as st
import plotter.HistogramPlotter as hplt

from reader import FileReader


class AppHistogramMetricsAnalyzer:

    def __init__(self, appName, statisticsDir):
        self.appName = appName
        self.statisticsDir = statisticsDir
        self.metricsMap = {}

    def analyzeMetrics(self, metrics):
        """
        :param metrics: [app.duration, stage0.duration, s0.task.jvmGcTime, ...]
        """
        statisticsFiles = os.listdir(self.statisticsDir)

        metricsSet = set(metrics)

        for file in statisticsFiles:
            if file.endswith("stat.txt"): # [RDDJoin-CMS-1-7G-stat.txt, RDDJoin-CMS-2-14G-stat.txt, ...]
                # [app.duration] mean = 224339.20, stdVar = 8311.91, median = 225233.00, min = 211999.00, quantile25 = 216682.50, quantile75 = 231549.00, max = 233837.00
                # -------------------------------------------------------------------[Stage 0]-------------------------------------------------------------------
                # [stage0.duration] mean = 42360.60, stdVar = 4069.63, median = 41404.00, min = 37094.00, quantile25 = 38942.50, quantile75 = 46257.00, max = 47801.00
                # [stage0.inputBytes] mean = 8588671743.00, stdVar = 0.00, median = 8588671743.00, min = 8588671743.00, quantile25 = 8588671743.00, quantile75 = 8588671743.00, max = 8588671743.00
                # [stage0.inputRecords] mean = 66000000.00, stdVar = 0.00, median = 66000000.00, min = 66000000.00, quantile25 = 66000000.00, quantile75 = 66000000.00, max = 66000000.00
                for line in FileReader.readLines(os.path.join(self.statisticsDir, file)):
                    metricName = line[line.find('[') + 1: line.find(']')]
                    if metricName in metricsSet:
                        if self.metricsMap.has_key(metricName):
                            self.metricsMap[metricName].addStatistics(line, file)
                        else:
                            statistics = st.Statistics()
                            statistics.addStatistics(line, file)
                            self.metricsMap[metricName] = statistics

    def plotMetrics(self, outputDir):

        if not os.path.exists(outputDir):
            os.mkdir(outputDir)

        for metricName, statistics in self.metricsMap.items():
            file = os.path.join(outputDir, metricName + ".pdf")
            hplt.HistogramPlotter.plotStatisticsByGCAlgo(statistics, metricName, 'Time (s)', file)
            print "[Done] The " + file + " has been generated!"



if __name__ == '__main__':

    appName = "GroupByRDD-0.5"
    statisticsDir = "/Users/xulijie/Documents/GCResearch/Experiments/profiles/" + appName + "/Statistics"
    outputDir = statisticsDir + "/figures-histo"
    metrics = [("app.duration", "Time (s)", 1000),

               ("stage0.duration", "Time (s)", 1000),
               ("stage0.jvmGCTime", "Time (s)", 1000),
               ("stage0.task.executorRunTime", "Time (s)", 1000),
               ("stage0.task.jvmGcTime", "Time (s)", 1000),
               ("stage0.task.memoryBytesSpilled", "MB", 1024 * 1024),
               ("stage0.task.diskBytesSpilled", "MB", 1024 * 1024),

               ("stage1.duration", "Time (s)", 1000),
               ("stage1.jvmGCTime", "Time (s)", 1000),
               ("stage1.task.executorRunTime", "Time (s)", 1000),
               ("stage1.task.jvmGcTime", "Time (s)", 1000),
               ("stage1.task.memoryBytesSpilled", "MB", 1024 * 1024),
               ("stage1.task.diskBytesSpilled", "MB", 1024 * 1024),

               # ("executor.memoryUsed", "GB", 1024 * 1024 * 1024),
               # ("executor.totalDuration", "Time (s)", 1000),
               # ("executor.totalGCTime", "Time (s)", 1000),
               # ("executor.maxMemory", "GB", 1024 * 1024 * 1024),

               ("executor.gc.footprint", "GB", 1024), # Maximal amount of memory allocated
               ("executor.gc.freedMemoryByGC", "GB", 1024), # Total amount of memory that has been freed
               ("executor.gc.accumPause", "Time (s)", 1), # Sum of all pauses due to any kind of GC
               ("executor.gc.gcPause", "Time (s)", 1), # This shows all stop-the-world pauses, that are not full gc pauses.
               ("executor.gc.throughput", "%", 1), # Time percentage the application was NOT busy with GC
               ("executor.gc.totalTime", "Time (s)", 1), # The duration of running executor
               ("executor.gc.gcPerformance", "MB/s", 1)] # Performance of minor collections

    appMetricsAnalyzer = AppHistogramMetricsAnalyzer(appName, statisticsDir)

    appMetricsAnalyzer.analyzeMetrics(metrics)
    appMetricsAnalyzer.plotMetrics(outputDir)
