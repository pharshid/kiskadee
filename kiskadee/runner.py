import shutil
import tempfile
import kiskadee
import kiskadee.queue
import kiskadee.analyzers
import kiskadee.model
import kiskadee.database
import kiskadee.helpers
import kiskadee.converter

running = True


def runner():
    """Runner entry point
    """
    database = kiskadee.database.Database()
    engine = database.engine
    session = database.session
    kiskadee.model.Base.metadata.create_all(engine)
    kiskadee.model.Base.metadata.bind = engine
    while running:
        if not kiskadee.queue.is_empty():
            kiskadee.logger.debug('RUNNER: dequeuing...')
            package = kiskadee.queue.dequeue_analysis()
            kiskadee.logger.debug('RUNNER: dequeued %s-%s from %s'
                                  % (package['name'],
                                     package['version'],
                                     package['plugin'].__name__))
            analysis_reports = analyze(package)
            if analysis_reports:
                kiskadee.logger.debug('RUNNER: Saving analysis %s' % str(package))
                all_analyses = '\n'.join(analysis_reports)
                pkg = session.query(kiskadee.model.Package).\
                      filter(kiskadee.model.Package.name == package['name']).\
                      first()
                pkg.versions[-1].has_analysis=True
                pkg.versions[-1].analysis=all_analyses
                session.add(pkg)
                session.commit()
                """ TODO: Not create a new session, make the session used by 
                monitor global. If we use another session, 
                session.merge() will not work. """
                #plugin = kiskadee.model.Plugin(name=package['plugin'].__name__)
                #_package = kiskadee.model.Package(name=package['name'])
                #version = kiskadee.model.Version(number=package['version'],
                #                                analysis=all_analyses,
                                                    #has_analysis=True)
                #session.merge(_package)
                #session.merge(plugin)
                #session.merge(version)
                kiskadee.logger.debug('DONE running analysis')
                # TODO: save reports in DB
                kiskadee.logger.debug(analysis_reports)
                kiskadee.logger.debug('end run')
            else:
                kiskadee.logger.debug('RUNNER: Something went wrong')
                kiskadee.logger.debug('RUNNER: analysis could not be generated')


def analyze(package):
    """ The package dict is in the queue. The keys are:
        plugin: the plugin module itself
        name: the package name
        version: the package version
        path: plugin default path for packages
        return: list with firehose reports
    """

    plugin = package['plugin'].Plugin()
    kiskadee.logger.info('ANALYSIS: Downloading {} '
            'source...'.format(package['name']))
    compressed_source = plugin.get_sources(package)
    if compressed_source:
        kiskadee.logger.debug('ANALYSIS: Downloaded!')
        kiskadee.logger.debug('ANALYSIS: Unpacking...')
        reports = []
        path = tempfile.mkdtemp()
        shutil.unpack_archive(compressed_source, path)
        with kiskadee.helpers.chdir(path):
            kiskadee.logger.debug('ANALYSIS: Unpacked!')
            analyzers = plugin.analyzers()
            for analyzer in analyzers:
                kiskadee.logger.debug('ANALYSIS: running %s ...' % analyzer)
                analysis = kiskadee.analyzers.run(analyzer, path)
                firehose_report = kiskadee.converter.to_firehose(analysis, analyzer)
                reports.append(str(firehose_report))
                kiskadee.logger.debug('ANALYSIS: DONE running %s' % analyzer)
            # TODO: remove compressed files and uncompressed files after the analysis
        return reports
    else:
        kiskadee.logger.debug('RUNNER: invalid source dict')
