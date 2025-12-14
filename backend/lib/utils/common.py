#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/4/29 16:07
@Author  : alexanderwu
@File    : common.py
"""
from __future__ import annotations

import ast
import contextlib
import csv
import inspect
import json
import os
import platform
import re
import sys
import traceback
from functools import partial
from pathlib import Path
from typing import Any, Callable, List, Literal, Optional, Tuple, Union
from urllib.parse import quote, unquote

import aiofiles
import chardet
from loguru import logger
from tenacity import RetryCallState, RetryError, _utils

# FlagPilot Adaption: relative import
from lib.utils.json_to_markdown import json_to_markdown

# FlagPilot Adaption: mock constants if they don't exist
MARKDOWN_TITLE_PREFIX = "##"
MESSAGE_ROUTE_TO_ALL = "@all"
from lib.utils.parse_docstring import remove_spaces  # re-use existing

def check_cmd_exists(command) -> int:
    """Check if command exists
    """
    if platform.system().lower() == "windows":
        check_command = "where " + command
    else:
        check_command = "command -v " + command + ' >/dev/null 2>&1 || { echo >&2 "no mermaid"; exit 1; }'
    result = os.system(check_command)
    return result


class OutputParser:
    @classmethod
    def parse_blocks(cls, text: str):
        # First split by "##"
        blocks = text.split(MARKDOWN_TITLE_PREFIX)

        block_dict = {}

        for block in blocks:
            if block.strip() != "":
                if "\n" in block:
                    block_title, block_content = block.split("\n", 1)
                else:
                    block_title, block_content = block, ""
                
                if block_title.strip().endswith(":"):
                    block_title = block_title.strip()[:-1]
                block_dict[block_title.strip()] = block_content.strip()

        return block_dict

    @classmethod
    def parse_code(cls, text: str, lang: str = "") -> str:
        pattern = rf"```{lang}.*?\s+(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            raise Exception
        return code

    @classmethod
    def parse_str(cls, text: str):
        text = text.split("=")[-1]
        text = text.strip().strip("'").strip('"')
        return text

    @classmethod
    def parse_file_list(cls, text: str) -> list[str]:
        pattern = r"\s*(.*=.*)?(\[.*\])"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            tasks_list_str = match.group(2)
            tasks = ast.literal_eval(tasks_list_str)
        else:
            tasks = text.split("\n")
        return tasks

    @staticmethod
    def parse_python_code(text: str) -> str:
        for pattern in (r"(.*?```python.*?\s+)?(?P<code>.*)(```.*?)", r"(.*?```python.*?\s+)?(?P<code>.*)"):
            match = re.search(pattern, text, re.DOTALL)
            if not match:
                continue
            code = match.group("code")
            if not code:
                continue
            with contextlib.suppress(Exception):
                ast.parse(code)
                return code
        raise ValueError("Invalid python code")

    @classmethod
    def parse_data(cls, data):
        block_dict = cls.parse_blocks(data)
        parsed_data = {}
        for block, content in block_dict.items():
            # try removing code markers
            try:
                content = cls.parse_code(text=content)
            except Exception:
                # try parsing list
                try:
                    content = cls.parse_file_list(text=content)
                except Exception:
                    pass
            parsed_data[block] = content
        return parsed_data

    @staticmethod
    def extract_content(text, tag="CONTENT"):
        extracted_content = re.search(rf"\[{tag}\](.*?)\[/{tag}\]", text, re.DOTALL)
        if extracted_content:
            return extracted_content.group(1).strip()
        else:
            raise ValueError(f"Could not find content between [{tag}] and [/{tag}]")


class CodeParser:
    @classmethod
    def parse_block(cls, block: str, text: str) -> str:
        blocks = cls.parse_blocks(text)
        for k, v in blocks.items():
            if block in k:
                return v
        return ""

    @classmethod
    def parse_blocks(cls, text: str):
        blocks = text.split("##")
        block_dict = {}
        for block in blocks:
            if block.strip() == "":
                continue
            if "\n" not in block:
                block_title = block
                block_content = ""
            else:
                block_title, block_content = block.split("\n", 1)
            block_dict[block_title.strip()] = block_content.strip()

        return block_dict

    @classmethod
    def parse_code(cls, text: str, lang: str = "", block: Optional[str] = None) -> str:
        if block:
            text = cls.parse_block(block, text)
        pattern = rf"```{lang}.*?\s+(.*?)\n```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            code = match.group(1)
        else:
            # logger.error(f"{pattern} not match")
            return text  # just assume original text is code
        return code


def remove_comments(code_str: str) -> str:
    """Remove comments from code."""
    pattern = r"(\".*?\"|\'.*?\')|(\#.*?$)"

    def replace_func(match):
        if match.group(2) is not None:
            return ""
        else:
            return match.group(1)

    clean_code = re.sub(pattern, replace_func, code_str, flags=re.MULTILINE)
    clean_code = os.linesep.join([s.rstrip() for s in clean_code.splitlines() if s.strip()])
    return clean_code


def any_to_str(val: Any) -> str:
    try:
        if isinstance(val, str):
            return val
        elif not callable(val):
            module = getattr(type(val), "__module__", "<unknown>")
            name = getattr(type(val), "__name__", "<unknown>")
            return f"{module}.{name}"
        else:
            module = getattr(val, "__module__", "<unknown>")
            name = getattr(val, "__name__", "<unknown>")
            return f"{module}.{name}"
    except Exception:
        return "<unknown>"
