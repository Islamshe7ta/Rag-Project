from enum import Enum


class VectorDBEnum(Enum):
    QDRANT = "qdrant"


class DistanceMethodsEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"
  