from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


ARUCO_DICTIONARY_CAPACITY: dict[str, int] = {
    "DICT_4X4_50": 50,
    "DICT_4X4_100": 100,
    "DICT_4X4_250": 250,
    "DICT_4X4_1000": 1000,
    "DICT_5X5_50": 50,
    "DICT_5X5_100": 100,
    "DICT_5X5_250": 250,
    "DICT_5X5_1000": 1000,
    "DICT_6X6_50": 50,
    "DICT_6X6_100": 100,
    "DICT_6X6_250": 250,
    "DICT_6X6_1000": 1000,
    "DICT_7X7_50": 50,
    "DICT_7X7_100": 100,
    "DICT_7X7_250": 250,
    "DICT_7X7_1000": 1000,
}


class PageConfig(BaseModel):
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)
    margin_top_mm: float = Field(ge=0)
    margin_right_mm: float = Field(ge=0)
    margin_bottom_mm: float = Field(ge=0)
    margin_left_mm: float = Field(ge=0)


class ArucoCornerOffset(BaseModel):
    x_mm: float = Field(default=0.0, ge=0)
    y_mm: float = Field(default=0.0, ge=0)


class ArucoCornerOffsets(BaseModel):
    top_left: ArucoCornerOffset = Field(default_factory=ArucoCornerOffset)
    top_right: ArucoCornerOffset = Field(default_factory=ArucoCornerOffset)
    bottom_left: ArucoCornerOffset = Field(default_factory=ArucoCornerOffset)
    bottom_right: ArucoCornerOffset = Field(default_factory=ArucoCornerOffset)


class ArucoConfig(BaseModel):
    dictionary_name: str
    marker_size_mm: float = Field(gt=0)
    corner_inset_mm: float = Field(ge=0)
    ids: list[int] = Field(min_length=4, max_length=4)
    corner_offsets_mm: ArucoCornerOffsets = Field(default_factory=ArucoCornerOffsets)

    @field_validator("ids")
    @classmethod
    def validate_unique_ids(cls, value: list[int]) -> list[int]:
        if len(set(value)) != len(value):
            raise ValueError("aruco ids must be unique")
        return value

    @model_validator(mode="after")
    def validate_dictionary_and_ids(self) -> "ArucoConfig":
        if self.dictionary_name not in ARUCO_DICTIONARY_CAPACITY:
            raise ValueError(f"unsupported aruco dictionary '{self.dictionary_name}'")

        capacity = ARUCO_DICTIONARY_CAPACITY[self.dictionary_name]
        for marker_id in self.ids:
            if marker_id < 0 or marker_id >= capacity:
                raise ValueError(
                    f"aruco id '{marker_id}' is out of range for {self.dictionary_name}"
                )
        return self


class BlockConfig(BaseModel):
    x_mm: float = Field(ge=0)
    y_mm: float = Field(ge=0)
    width_mm: float = Field(gt=0)
    height_mm: float = Field(gt=0)


class BubbleGroupConfig(BaseModel):
    group_id: str = Field(min_length=1)
    rows: int = Field(gt=0)
    cols: int = Field(gt=0)
    num_questions: int | None = Field(default=None, gt=0)
    question_start_number: int = Field(default=1, ge=1)
    radius_mm: float = Field(gt=0)
    spacing_x_mm: float = Field(gt=0)
    spacing_y_mm: float = Field(gt=0)
    offset_x_mm: float = Field(ge=0)
    offset_y_mm: float = Field(ge=0)
    column_labels: list[str] | None = None

    @model_validator(mode="after")
    def validate_column_labels(self) -> "BubbleGroupConfig":
        if self.column_labels is None:
            return self
        if len(self.column_labels) != self.cols:
            raise ValueError("column_labels length must match cols")
        for label in self.column_labels:
            if not label or not label.strip():
                raise ValueError("column_labels cannot contain empty values")
        return self


class BubbleLabelStyle(BaseModel):
    gray_level: float = Field(default=0.78, ge=0.0, le=1.0)
    font_name: str = Field(default="Helvetica")
    font_size_pt: float = Field(default=8.0, gt=0.0)


class QuestionNumberStyle(BaseModel):
    enabled: bool = True
    center_gap_mm: float = Field(default=10.0, gt=0.0)
    gray_level: float = Field(default=0.40, ge=0.0, le=1.0)
    font_name: str = Field(default="Helvetica")
    font_size_pt: float = Field(default=8.0, gt=0.0)


class BubbleConfig(BaseModel):
    groups: list[BubbleGroupConfig] = Field(min_length=1)
    label_style: BubbleLabelStyle = Field(default_factory=BubbleLabelStyle)
    question_number_style: QuestionNumberStyle = Field(default_factory=QuestionNumberStyle)

    @model_validator(mode="after")
    def validate_unique_group_ids(self) -> "BubbleConfig":
        seen: set[str] = set()
        for group in self.groups:
            if group.group_id in seen:
                raise ValueError(f"duplicate bubble group_id '{group.group_id}'")
            seen.add(group.group_id)
        return self


class OutputConfig(BaseModel):
    template_id: str = Field(min_length=1)
    version: str = Field(min_length=1)


class TemplateConfig(BaseModel):
    page_config: PageConfig
    aruco_config: ArucoConfig
    block_config: BlockConfig
    bubble_config: BubbleConfig
    output_config: OutputConfig

    @model_validator(mode="after")
    def validate_page_margins(self) -> "TemplateConfig":
        page = self.page_config
        if page.margin_left_mm + page.margin_right_mm >= page.width_mm:
            raise ValueError("horizontal margins exceed page width")
        if page.margin_top_mm + page.margin_bottom_mm >= page.height_mm:
            raise ValueError("vertical margins exceed page height")
        return self


class MarkerPlacement(BaseModel):
    marker_id: int
    corner: Literal["top_left", "top_right", "bottom_left", "bottom_right"]
    center_x_mm: float
    center_y_mm: float
    size_mm: float


class BubblePlacement(BaseModel):
    bubble_id: str
    group_id: str
    row: int
    col: int
    label: str
    center_x_mm: float
    center_y_mm: float
    radius_mm: float


class QuestionNumberPlacement(BaseModel):
    group_id: str
    row: int
    question_number: int
    center_x_mm: float
    center_y_mm: float


class QuestionItem(BaseModel):
    group_id: str
    row: int
    question_number: int
    number_center_x_mm: float
    number_center_y_mm: float
    options: list[BubblePlacement]


class BlockGeometry(BaseModel):
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float


class TemplateLayout(BaseModel):
    template_id: str
    version: str
    aruco_dictionary_name: str
    page: PageConfig
    printable_area: BlockGeometry
    main_block_bbox: BlockGeometry
    block: BlockGeometry
    aruco_markers: list[MarkerPlacement]
    bubbles: list[BubblePlacement]
    bubble_label_style: BubbleLabelStyle
    question_numbers: list[QuestionNumberPlacement]
    question_number_style: QuestionNumberStyle
    question_items: list[QuestionItem]
