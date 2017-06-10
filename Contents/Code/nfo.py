from datetime import datetime
from helper import get_actor_thumb


# noinspection PyClassHasNoInit
class NfoUtil:
    @staticmethod
    def get_text(element, tag, default=None):
        """
        Get the text of the first child tag's text
        :type element: _Element
        :type tag: str
        :param element:
        :param tag:
        :param default:
        :rtype: str
        :return:
        """
        tag_element = element.find(tag)
        text = default
        if tag_element is not None:
            text = tag_element.text
        return text

    @staticmethod
    def get_set(element, tag):
        tag_elements = element.findall(tag)
        tag_set = set()
        for tag_element in tag_elements:
            tag_text = tag_element.text
            if not tag_text:
                tag_set.add(tag_text)
        return tag_set

    @staticmethod
    def get_date(element, tag):
        text = NfoUtil.get_text(element, tag)
        if text is None:
            return None
        try:
            date = datetime.strptime(text, "%Y-%m-%d")
        except ValueError:
            return None
        return date

    @staticmethod
    def get_actors(element, tag):
        tag_elements = element.findall(tag)
        actors = []
        for tag_element in tag_elements:
            name = NfoUtil.get_text(tag_element, "name", "")
            role = NfoUtil.get_text(tag_element, "role", "")
            thumb = NfoUtil.get_text(tag_element, "thumb", "")
            if not thumb:
                thumb = get_actor_thumb
            actors.append((name, role, thumb))
        return actors

    @staticmethod
    def set_metadata_value_field(source, metadata, field, none_check=True):
        source_value = getattr(source, field)
        if not none_check or source_value is not None:
            setattr(metadata, field, source_value)

    @staticmethod
    def set_metadata_set_field(source, metadata, field):
        source_set = getattr(source, field)
        metadata_set = getattr(metadata, field)
        if source_set is not None and metadata_set is not None:
            metadata_set.clear()
            for value in source_set:
                metadata_set.add(value)

    @staticmethod
    def set_metadata_set_name_field(source, metadata, field):
        source_set = getattr(source, field)
        metadata_set = getattr(metadata, field)
        if source_set is not None and metadata_set is not None:
            metadata_set.clear()
            for value in source_set:
                metadata_set.new().name = value


class Nfo:
    def __init__(self, root_element):
        self.root_element = root_element  # type: _Element
        self.value_fields = []
        self.set_fields = []

    def get_text_from_root(self, tag):
        return NfoUtil.get_text(self.root_element, tag)

    def get_set_from_root(self, tag):
        return NfoUtil.get_set(self.root_element, tag)

    def get_date_from_root(self, tag):
        return NfoUtil.get_date(self.root_element, tag)

    def get_rating_from_root(self, tag):
        rating_str = self.get_text_from_root(tag)
        if rating_str is None:
            return None
        # Round rating to 1 decimal place
        rating = round(float(rating_str), 1)
        return rating

    def set_metadata(self, metadata):
        for field in self.value_fields:
            NfoUtil.set_metadata_value_field(self, metadata, field)

        for field in self.set_fields:
            NfoUtil.set_metadata_set_field(self, metadata, field)

    def __repr__(self):
        repr_str = ""
        for field in self.value_fields:
            repr_str += "%s: %s\n" % (field, getattr(self, field))
        for field in self.set_fields:
            repr_str += "%s: %s\n" % (field, getattr(self, field))
        return repr_str


class TvNfo(Nfo):
    def __init__(self, root_element):
        Nfo.__init__(self, root_element)
        self.value_fields = [
            "title",
            "title_sort",
            "original_title",
            "content_rating",
            "studio",
            "originally_available_at",
            "tagline",
            "summary",
            "rating"
        ]
        self.set_fields = [
            "genres",
            "collections"
        ]
        self.title = self.extract_title()  # type: str
        self.title_sort = self.extract_title_sort()  # type: str
        self.original_title = self.extract_original_title()  # type: str
        self.content_rating = self.extract_content_rating()  # type: str
        self.studio = self.extract_studio()  # type: str
        self.originally_available_at = self.extract_originally_available_at()  # type: datetime
        # Plex does not support
        self.tagline = self.extract_tagline()  # type: str
        self.summary = self.extract_summary()  # type: str
        self.rating = self.extract_rating()  # type: float
        self.genres = self.extract_genres()  # type: set
        self.collections = self.extract_collections()  # type: set
        self.actors = self.extract_actors()

    def extract_title(self):
        return self.get_text_from_root("title")

    def extract_originally_available_at(self):
        return self.get_date_from_root("premiered")

    def extract_title_sort(self):
        return self.get_text_from_root("sorttitle")

    def extract_original_title(self):
        return self.get_text_from_root("originaltitle")

    def extract_content_rating(self):
        return self.get_text_from_root("mpaa")

    def extract_studio(self):
        return self.get_text_from_root("studio")

    def extract_tagline(self):
        return self.get_text_from_root("tagline")

    def extract_summary(self):
        return self.get_text_from_root("plot")

    def extract_rating(self):
        return self.get_rating_from_root("rating")

    def extract_genres(self):
        return self.get_set_from_root("genre")

    def extract_collections(self):
        return self.get_set_from_root("set")

    def extract_actors(self):
        return NfoUtil.get_actors(self.root_element, "actor")

    def set_metadata(self, metadata):
        Nfo.set_metadata(self, metadata)
        self.set_metadata_actors(metadata)

    def set_metadata_actors(self, metadata):
        metadata.roles.clear()
        for actor in self.actors:
            role = metadata.roles.new()
            role.name, role.role, role.photo = actor


class EpisodeNfo(Nfo):
    def __init__(self, root_element):
        Nfo.__init__(self, root_element)
        self.value_fields = [
            "title",
            "content_rating",
            "originally_available_at",
            "summary",
            "rating"
        ]
        self.title = self.extract_title()  # type: str
        self.content_rating = self.extract_content_rating()  # type: str
        self.originally_available_at = self.extract_originally_available_at()  # type: datetime
        self.summary = self.extract_summary()  # type: str
        self.rating = self.extract_rating()  # type: float
        self.producers = self.extract_producers()  # type: set
        self.writers = self.extract_writers()  # type: set
        self.guest_stars = self.extract_guest_stars()  # type: set
        self.directors = self.extract_directors()  # type: set

    def extract_title(self):
        return self.get_text_from_root("title")

    def extract_content_rating(self):
        return self.get_text_from_root("mpaa")

    def extract_originally_available_at(self):
        return self.get_date_from_root("aired")

    def extract_summary(self):
        return self.get_text_from_root("plot")

    def extract_rating(self):
        return self.get_rating_from_root("rating")

    def extract_producers(self):
        return self.get_set_from_root("producer")

    def extract_writers(self):
        return self.get_set_from_root("writer")

    def extract_guest_stars(self):
        return self.get_set_from_root("guest")

    def extract_directors(self):
        return self.get_set_from_root("director")

    def set_metadata(self, metadata):
        Nfo.set_metadata(self, metadata)
        NfoUtil.set_metadata_set_name_field(self, metadata, "producers")
        NfoUtil.set_metadata_set_name_field(self, metadata, "writers")
        NfoUtil.set_metadata_set_name_field(self, metadata, "guest_stars")
        NfoUtil.set_metadata_set_name_field(self, metadata, "directors")


class MovieNfo(TvNfo):
    def __init__(self, root_element):
        TvNfo.__init__(self, root_element)
        self.producers = self.extract_producers()  # type: set
        self.writers = self.extract_writers()  # type: set
        self.guest_stars = self.extract_guest_stars()  # type: set
        self.directors = self.extract_directors()  # type: set

    def extract_originally_available_at(self):
        return self.get_date_from_root("releasedate")

    def extract_producers(self):
        return self.get_set_from_root("producer")

    def extract_writers(self):
        return self.get_set_from_root("writer")

    def extract_guest_stars(self):
        return self.get_set_from_root("guest")

    def extract_directors(self):
        return self.get_set_from_root("director")

    def set_metadata(self, metadata):
        TvNfo.set_metadata(self, metadata)
        NfoUtil.set_metadata_set_name_field(self, metadata, "producers")
        NfoUtil.set_metadata_set_name_field(self, metadata, "writers")
        NfoUtil.set_metadata_set_name_field(self, metadata, "guest_stars")
        NfoUtil.set_metadata_set_name_field(self, metadata, "directors")