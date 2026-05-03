import logging
from types import SimpleNamespace
from unittest.mock import Mock, patch

from mezon.models import (
    AnimationConfig,
    InputFieldOption,
    RadioFieldOption,
    SelectFieldOption,
)
from mezon.structures.interactive_message import InteractiveBuilder
from mezon.utils.logger import (
    ColoredFormatter,
    disable_logging,
    enable_logging,
    get_logger,
    setup_logger,
)


class TestLoggerAndInteractive:
    def test_colored_formatter_supports_color_branches(self):
        formatter = ColoredFormatter("%(message)s", use_colors=False)

        with patch("mezon.utils.logger.sys.stderr", SimpleNamespace()):
            assert formatter._supports_color() is False

        with patch(
            "mezon.utils.logger.sys.stderr", SimpleNamespace(isatty=lambda: False)
        ):
            assert formatter._supports_color() is False

        fake_kernel32 = Mock()
        fake_kernel32.GetStdHandle.return_value = 1
        fake_kernel32.SetConsoleMode.return_value = 1
        fake_ctypes = SimpleNamespace(windll=SimpleNamespace(kernel32=fake_kernel32))
        with (
            patch(
                "mezon.utils.logger.sys.stderr", SimpleNamespace(isatty=lambda: True)
            ),
            patch("platform.system", return_value="Windows"),
            patch.dict("sys.modules", {"ctypes": fake_ctypes}),
        ):
            assert formatter._supports_color() is True
            fake_kernel32.SetConsoleMode.assert_called_once_with(1, 7)

        with (
            patch(
                "mezon.utils.logger.sys.stderr", SimpleNamespace(isatty=lambda: True)
            ),
            patch("platform.system", side_effect=RuntimeError("boom")),
        ):
            assert formatter._supports_color() is True

    def test_setup_logger_reuses_existing_handler(self):
        logger = setup_logger(name="mezon-test-reuse", use_colors=False)
        handler_count = len(logger.handlers)

        same_logger = setup_logger(
            name="mezon-test-reuse", log_level=logging.ERROR, use_colors=False
        )

        assert same_logger is logger
        assert len(logger.handlers) == handler_count
        assert logger.level == logging.ERROR

    def test_setup_logger_uses_custom_formats(self):
        logger = setup_logger(
            name="mezon-test-format",
            log_level=logging.WARNING,
            log_format="%(levelname)s|%(message)s",
            date_format="%H:%M",
            use_colors=False,
        )

        handler = logger.handlers[-1]
        assert isinstance(handler.formatter, ColoredFormatter)
        assert handler.formatter._style._fmt == "%(levelname)s|%(message)s"
        assert handler.formatter.datefmt == "%H:%M"

    def test_get_random_color_is_applied_by_default(self):
        with patch(
            "mezon.structures.interactive_message.random.randint", return_value=0xABCDEF
        ):
            interactive = InteractiveBuilder().build()

        assert interactive["color"] == "#abcdef"

    def test_colored_formatter_formats_plain_and_colored(self):
        plain = ColoredFormatter("%(levelname)s %(message)s", use_colors=False)
        record = logging.LogRecord(
            "mezon", logging.INFO, __file__, 1, "hello", (), None
        )
        assert plain.format(record) == "INFO hello"

        colored = ColoredFormatter("%(levelname)s %(message)s", use_colors=True)
        colored.use_colors = True
        formatted = colored.format(record)
        assert "hello" in formatted
        assert "\033[" in formatted

    def test_setup_get_disable_and_enable_logging(self):
        logger = setup_logger(name="mezon-test", use_colors=False)
        fetched = get_logger("mezon-test")
        disable_logging("mezon-test")
        assert fetched.disabled is True
        enable_logging("mezon-test", logging.DEBUG)
        assert fetched.disabled is False
        assert fetched.level == logging.DEBUG
        assert logger is fetched

    def test_interactive_builder_full_workflow(self):
        with patch(
            "mezon.structures.interactive_message.random.randint", return_value=0x123456
        ):
            builder = InteractiveBuilder("Welcome")

        interactive = (
            builder.set_color("#ffffff")
            .set_title("Title")
            .set_url("https://example.com")
            .set_author(
                "Author",
                icon_url="https://example.com/a.png",
                url="https://example.com",
            )
            .set_description("Description")
            .set_thumbnail("https://example.com/thumb.png")
            .set_image("https://example.com/image.png")
            .set_footer("Footer", icon_url="https://example.com/footer.png")
            .add_field("Name", "Value", inline=True)
            .add_input_field(
                "input-1",
                "Input",
                "placeholder",
                InputFieldOption(defaultValue="x", type="text", textarea=True),
                "desc",
            )
            .add_select_field(
                "select-1",
                "Select",
                [SelectFieldOption(label="One", value="1")],
                value_selected=SelectFieldOption(label="One", value="1"),
                description="select-desc",
            )
            .add_radio_field(
                "radio-1",
                "Radio",
                [RadioFieldOption(label="A", value="a")],
                description="radio-desc",
                max_options=2,
            )
            .add_datepicker_field("date-1", "Date", "date-desc")
            .add_animation(
                "anim-1",
                AnimationConfig(
                    url_image="https://example.com/i.png",
                    url_position="https://example.com/p.json",
                    pool=["a", "b"],
                ),
                name="Animation",
                description="anim-desc",
            )
            .build()
        )

        assert interactive["title"] == "Title"
        assert interactive["url"] == "https://example.com"
        assert interactive["author"]["name"] == "Author"
        assert interactive["thumbnail"]["url"].endswith("thumb.png")
        assert interactive["image"]["width"] == "auto"
        assert len(interactive["fields"]) == 6
        assert interactive["fields"][1]["inputs"]["component"]["defaultValue"] == "x"
        assert (
            interactive["fields"][2]["inputs"]["component"]["options"][0]["label"]
            == "One"
        )
        assert interactive["fields"][3]["inputs"]["max_options"] == 2
        assert interactive["fields"][4]["inputs"]["type"] is not None
        assert interactive["fields"][5]["inputs"]["type"] is not None
