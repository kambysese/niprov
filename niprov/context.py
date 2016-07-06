from niprov.dependencies import Dependencies
from niprov.config import Configuration
import niprov


class ProvenanceContext(object):

    def __init__(self):
        self.config = Configuration()
        self.deps = Dependencies(self.config)

    def add(self, filepath, transient=False, provenance=None):
        """See :py:mod:`niprov.adding`  """
        return niprov.adding.add(filepath, transient, provenance, self.deps)

    def approve(self, filepath):
        """See :py:mod:`niprov.approval`  """
        return niprov.approval.approve(filepath, dependencies=self.deps)

    def backup(self, *args, **kwargs):
        """See :py:mod:`niprov.exporting`  """
        return niprov.exporting.backup(*args, dependencies=self.deps, **kwargs)

    def compare(self, file1, file2):
        """See :py:mod:`niprov.comparing`  """
        return niprov.comparing.compare(file1, file2, dependencies=self.deps)

    def discover(self, root):
        """See :py:mod:`niprov.discovery`  """
        return niprov.discovery.discover(root, dependencies=self.deps)

    def export(self, *args, **kwargs):
        """See :py:mod:`niprov.exporting`  """
        return niprov.exporting.export(*args, dependencies=self.deps, **kwargs)

    def get(self):
        """See :py:mod:`niprov.querying`  """
        return self.deps.getQuery()

    def importp(self, *args, **kwargs):
        """See :py:mod:`niprov.importing`  """
        return niprov.importing.importp(*args, dependencies=self.deps, **kwargs)

    def inspect(self, location):
        """See :py:mod:`niprov.inspection`  """
        return niprov.inspection.inspect(location, dependencies=self.deps)

    def log(self, *args, **kwargs):
        """See :py:mod:`niprov.logging`  """
        return niprov.logging.log(*args, dependencies=self.deps, **kwargs)

    def markForApproval(self, files):
        """See :py:mod:`niprov.approval`  """
        return niprov.approval.markForApproval(files, dependencies=self.deps)

    def markedForApproval(self):
        """See :py:mod:`niprov.approval`  """
        return niprov.approval.markedForApproval(dependencies=self.deps)

    def print_(self, *args, **kwargs):
        """See :py:mod:`niprov.exporting`  """
        return niprov.exporting.print_(*args, dependencies=self.deps, **kwargs)

    def renameDicoms(self, dicomdir):
        """See :py:mod:`niprov.renaming`  """
        return niprov.renaming.renameDicoms(dicomdir, dependencies=self.deps)

    def record(self, *args, **kwargs):
        """See :py:mod:`niprov.recording`  """
        return niprov.recording.record(*args, dependencies=self.deps, **kwargs)

    def search(self, text):
        """See :py:mod:`niprov.searching`  """
        return niprov.searching.search(text, dependencies=self.deps)

    def selectApproved(self, files):
        """See :py:mod:`niprov.approval`  """
        return niprov.approval.selectApproved(files, dependencies=self.deps)

    def view(self, *args, **kwargs):
        """See :py:mod:`niprov.exporting`  """
        return niprov.exporting.view(*args, dependencies=self.deps, **kwargs)
