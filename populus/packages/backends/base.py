class BasePackageBackend(object):
    project = None
    settings = None

    def __init__(self, project, settings):
        self.project = project
        self.settings = settings
        self.setup_backend()

    def setup_backend(self):
        pass

    #
    # Read API primarily for package installation
    #
    def can_translate_package_identifier(self, package_identifier):
        """
        Returns `True` or `False` as to whether this backend is capable of
        translating this identifier.
        """
        return False

    def translate_package_identifier(self, package_identifier):
        """
        Returns the translated result of the package identifier.  This should
        always be returned as an iterable so that *special* identifiers can end
        up being translated to mean (install multiple packages).

        Translation is the process of taking a package identifier and
        converting it into another more basic format.  The translation of
        identifiers is a directed acyclic graph which when successful results
        in an identifier that can be resolved to a release lockfile.
        """
        raise NotImplementedError("Must be implemented by subclasses")

    def can_resolve_to_release_lockfile(self, package_identifier):
        """
        Returns `True` or `False` as to whether this backend is capable of
        resolving this identifier into a release lockfile for this package.
        """
        return False

    def resolve_to_release_lockfile(self, package_identifier):
        """
        Returns the release lockfile or raises
        `populus.packages.exceptions.UnresolvablePackageIdentifier` if the
        identifier cannot be resolved.
        """
        raise NotImplementedError("Must be implemented by subclasses")

    def can_resolve_package_source_tree(self, release_lockfile):
        return False

    def resolve_package_source_tree(self, release_lockfile):
        raise NotImplementedError("Must be implemented by subclasses")

    #
    # Write API primarily for publishing
    #
    def can_persist_package_file(self, file_path):
        """
        Returns `True` or `False` as to whether this backend can persist the
        provided file to whatever persistence source it uses.
        """
        return False

    def persist_package_file(self, file_path):
        """
        Persists the provided file to this backends persistence layer.
        """
        raise NotImplementedError("Must be implemented by subclasses")

    def can_publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        """
        Returns `True` or `False` as to whether this backend can publish this
        release lockfile.
        """
        return False

    def publish_release_lockfile(self, release_lockfile, release_lockfile_uri):
        """
        Publishes the release lockfile.
        """
        raise NotImplementedError("Must be implemented by subclasses")
