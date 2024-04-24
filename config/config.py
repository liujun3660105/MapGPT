import os
from typing import TYPE_CHECKING, List, Optional,Union
from dataclasses import dataclass, field, fields,asdict
from Utils.parameterUtils import _get_dataclass_print_str,_dict_to_command_args

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGDIR = os.getenv("MAPGPT_LOG_DIR", os.path.join(ROOT_PATH, "logs"))

@dataclass
class Config:
    LOCAL_DB_TYPE = os.getenv("LOCAL_DB_TYPE", "postgresql")
    LOCAL_DB_HOST = os.getenv("LOCAL_DB_HOST")
    # LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH", "data/default_sqlite.db")
    LOCAL_DB_NAME = os.getenv("LOCAL_DB_NAME", "mapgpt")
    LOCAL_DB_PORT = int(os.getenv("LOCAL_DB_PORT", 5432))
    LOCAL_DB_USER = os.getenv("LOCAL_DB_USER", "root")
    LOCAL_DB_PASSWORD = os.getenv("LOCAL_DB_PASSWORD", "aa123456")
    LOCAL_DB_POOL_SIZE = int(os.getenv("LOCAL_DB_POOL_SIZE", 10))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE=os.getenv("OPENAI_API_BASE")
    EMBEDDING_PATH = os.getenv('EMBEDDING_PATH')
    BAIDU_API_KEY = os.getenv("BAIDU_API_KEY")
    BAIDU_SECRET_KEY = os.getenv("BAIDU_SECRET_KEY")
    MILVUS_HOST = os.getenv("MILVUS_HOST")
    MILVUS_PORT = os.getenv("MILVUS_PORT")
    MILVUS_USERNAME = os.getenv("MILVUS_USERNAME")
    MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
    def __post_init__(self):
        if self.LOCAL_DB_HOST is None:
            self.LOCAL_DB_HOST = "127.0.0.1"
            



@dataclass
class BaseParameters:
    @classmethod
    def from_dict(
        cls, data: dict, ignore_extra_fields: bool = False
    ) -> "BaseParameters":
        """Create an instance of the dataclass from a dictionary.

        Args:
            data: A dictionary containing values for the dataclass fields.
            ignore_extra_fields: If True, any extra fields in the data dictionary that are
                not part of the dataclass will be ignored.
                If False, extra fields will raise an error. Defaults to False.
        Returns:
            An instance of the dataclass with values populated from the given dictionary.

        Raises:
            TypeError: If `ignore_extra_fields` is False and there are fields in the
                           dictionary that aren't present in the dataclass.
        """
        all_field_names = {f.name for f in fields(cls)}
        if ignore_extra_fields:
            data = {key: value for key, value in data.items() if key in all_field_names}
        else:
            extra_fields = set(data.keys()) - all_field_names
            if extra_fields:
                raise TypeError(f"Unexpected fields: {', '.join(extra_fields)}")
        return cls(**data)

    def update_from(self, source: Union["BaseParameters", dict]) -> bool:
        """
        Update the attributes of this object using the values from another object (of the same or parent type) or a dictionary.
        Only update if the new value is different from the current value and the field is not marked as "fixed" in metadata.

        Args:
            source (Union[BaseParameters, dict]): The source to update from. Can be another object of the same type or a dictionary.

        Returns:
            bool: True if at least one field was updated, otherwise False.
        """
        updated = False  # Flag to indicate whether any field was updated
        if isinstance(source, (BaseParameters, dict)):
            for field_info in fields(self):
                # Check if the field has a "fixed" tag in metadata
                tags = field_info.metadata.get("tags")
                tags = [] if not tags else tags.split(",")
                if tags and "fixed" in tags:
                    continue  # skip this field
                # Get the new value from source (either another BaseParameters object or a dict)
                new_value = (
                    getattr(source, field_info.name)
                    if isinstance(source, BaseParameters)
                    else source.get(field_info.name, None)
                )

                # If the new value is not None and different from the current value, update the field and set the flag
                if new_value is not None and new_value != getattr(
                    self, field_info.name
                ):
                    setattr(self, field_info.name, new_value)
                    updated = True
        else:
            raise ValueError(
                "Source must be an instance of BaseParameters (or its derived class) or a dictionary."
            )

        return updated

    def __str__(self) -> str:
        return _get_dataclass_print_str(self)

    def to_command_args(self, args_prefix: str = "--") -> List[str]:
        """Convert the fields of the dataclass to a list of command line arguments.

        Args:
            args_prefix: args prefix
        Returns:
            A list of strings where each field is represented by two items:
            one for the field name prefixed by args_prefix, and one for its value.
        """
        return _dict_to_command_args(asdict(self), args_prefix=args_prefix)

            
@dataclass
class WebServerParameters(BaseParameters):
    host: Optional[str] = field(
        default="0.0.0.0", metadata={"help": "Webserver deploy host"}
    )
    port: Optional[int] = field(
        default=5002, metadata={"help": "Webserver deploy port"}
    )
    log_level: Optional[str] = field(
        default=None,
        metadata={
            "help": "Logging level",
            "valid_values": [
                "FATAL",
                "ERROR",
                "WARNING",
                "WARNING",
                "INFO",
                "DEBUG",
                "NOTSET",
            ],
        },
    )
    log_file: Optional[str] = field(
        default="mapgpt_webserver.log",
        metadata={
            "help": "The filename to store log",
        },
    )