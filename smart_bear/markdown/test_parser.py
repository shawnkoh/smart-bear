from parsy import string
from pytest import raises
from rich.pretty import pprint

from smart_bear.intelligence.test_utilities import assert_that
from smart_bear.markdown.lexer import HeadingPrefix, Tag, lexer
from smart_bear.markdown.parser import (
    Answer,
    Backlink,
    BacklinkBlock,
    BasicPrompt,
    Break,
    Cloze,
    ClozePrompt,
    FencedCodeBlock,
    Heading,
    Paragraph,
    Question,
    Root,
    Spacer,
    Text,
    Title,
    answer,
    backlink,
    backlink_block,
    basic_prompt,
    block,
    cloze,
    cloze_prompt,
    contents,
    fenced_code_block,
    heading,
    paragraph,
    parser,
    question,
    text,
    title,
)


def test_text():
    tokens = lexer.parse("text")
    assert_that(
        text.parse(tokens),
        Text("text"),
    )


def test_contents():
    tokens = lexer.parse("content\ncontent")
    assert contents.parse(tokens) == [
        Text("content"),
        Break(),
        Text("content"),
    ]


def test_question():
    tokens = lexer.parse("Q: Question\nExtended")
    expected = Question(
        [
            Text("Question"),
            Break(),
            Text("Extended"),
        ]
    )
    assert_that(
        question.parse(tokens),
        expected,
    )


def test_question_answer():
    tokens = lexer.parse("Q: Question\nExtended\nA: Answer")
    expected = Question(
        [
            Text("Question"),
            Break(),
            Text("Extended"),
        ]
    )
    assert_that(
        question.parse_partial(tokens)[0],
        expected,
    )


def test_answer():
    tokens = lexer.parse("A: Answer\nExtended")
    expected = Answer(
        [
            Text("Answer"),
            Break(),
            Text("Extended"),
        ]
    )
    assert_that(
        answer.parse(tokens),
        expected,
    )


def test_basic_prompt():
    given = lexer.parse("Q: Question\nExtended\nA: Answer\nExtended")
    expected = BasicPrompt(
        question=Question(
            [
                Text("Question"),
                Break(),
                Text("Extended"),
            ]
        ),
        answer=Answer(
            [
                Text("Answer"),
                Break(),
                Text("Extended"),
            ]
        ),
    )
    assert_that(
        basic_prompt.parse(given),
        expected,
    )


def test_basic_prompt_question_only():
    given = lexer.parse("Q: Question\nExtended")
    expected = BasicPrompt(
        question=Question(
            [
                Text("Question"),
                Break(),
                Text("Extended"),
            ]
        ),
        answer=None,
    )
    assert_that(
        basic_prompt.parse(given),
        expected,
    )


def test_cloze():
    given = lexer.parse("{{abc}}")
    expected = Cloze(
        [
            Text("abc"),
        ]
    )
    assert_that(
        cloze.parse(given),
        expected,
    )


def test_cloze_text():
    tokens = lexer.parse("abc")
    expected = [Text("abc")]
    with raises(Exception) as _:
        cloze.parse(tokens)


def test_cloze_space():
    given = lexer.parse("{{ abc }}")
    expected = Cloze(
        [
            Text(" abc "),
        ]
    )
    assert_that(
        cloze.parse(given),
        expected,
    )


def test_cloze_lspace():
    given = lexer.parse("{{ abc}}")
    expected = Cloze(
        [
            Text(" abc"),
        ]
    )
    assert_that(cloze.parse(given), expected)


def test_cloze_rspace():
    given = lexer.parse("{{abc }}")
    expected = Cloze(
        [
            Text("abc "),
        ]
    )
    assert_that(cloze.parse(given), expected)


def test_cloze_prompt():
    given = lexer.parse("Some text {{with clozes}}")
    expected = ClozePrompt(
        [
            Text("Some text "),
            Cloze(
                [
                    Text("with clozes"),
                ]
            ),
        ]
    )
    pprint(cloze_prompt.parse_partial(given))
    assert_that(cloze_prompt.parse(given), expected)


def test_cloze_prompt_fails():
    tokens = lexer.parse("Some text")
    with raises(Exception) as _:
        cloze_prompt.parse(tokens)


def test_paragraph_simple():
    tokens = lexer.parse("Simple")
    expected = Paragraph(
        [
            Text("Simple"),
        ]
    )
    assert_that(paragraph.parse(tokens), expected)


def test_paragraph_multi():
    tokens = lexer.parse("Simple\n\nHello\n")
    expected = Paragraph(
        [
            Text("Simple"),
        ]
    )
    assert_that(paragraph.parse_partial(tokens)[0], expected)


def test_paragraph_backlink():
    tokens = lexer.parse("* [[How]]")
    expected = Paragraph(
        [
            Text("* "),
            Backlink(Text("How")),
        ]
    )
    assert_that(paragraph.parse(tokens), expected)


def test_concat():
    given = ""
    expected = ""
    _parser = string("[").many().concat() + string("]").many().concat()
    pprint(_parser.parse(given))
    assert given == expected


def test_title():
    tokens = lexer.parse("Simple")
    expected = Title(Text("Simple"))
    assert_that(title.parse(tokens), expected)


def test_title_eol():
    tokens = lexer.parse("Simple\nSimple")
    expected = Title(Text("Simple"))
    assert_that(title.parse_partial(tokens)[0], expected)


def test_parser():
    tokens = lexer.parse(
        """# Smart Bear
Paragraph 1

Paragraph 2"""
    )
    expected = Root(
        title=Title(Text("# Smart Bear")),
        children=[
            Paragraph(
                [
                    Text("Paragraph 1"),
                ]
            ),
            Spacer(
                [
                    Break(),
                    Break(),
                ]
            ),
            Paragraph(
                [
                    Text("Paragraph 2"),
                ]
            ),
        ],
    )
    assert_that(parser.parse(tokens), expected)


def test_backlink():
    tokens = lexer.parse("[[backlink]]")
    expected = Backlink(
        Text("backlink"),
    )
    assert_that(backlink.parse(tokens), expected)


def test_backlink_fails():
    tokens = lexer.parse("m[[backlink]]")
    with raises(Exception) as _:
        backlink.parse(tokens)


def test_backlink_spaced_fails():
    tokens = lexer.parse(" [[backlink]]")
    with raises(Exception) as _:
        backlink.parse(tokens)


def test_paragraph_tag():
    tokens = lexer.parse("#g2")
    expected = Paragraph(
        [
            Tag("g2"),
        ],
    )
    assert_that(paragraph.parse(tokens), expected)


def test_backlink_block():
    tokens = lexer.parse("## Backlinks\nSome Stuff")
    expected = BacklinkBlock(
        Paragraph(
            [
                Text("Some Stuff"),
            ]
        )
    )
    assert_that(backlink_block.parse(tokens), expected)


def test_fenced_code_block():
    tokens = lexer.parse("```\nBlah\n```")
    expected = FencedCodeBlock(
        info_string=None,
        children=[
            Text("Blah"),
        ],
    )
    assert_that(fenced_code_block.parse(tokens), expected)


def test_fenced_code_block_info_string():
    tokens = lexer.parse("```swift\nBlah\n```")
    expected = FencedCodeBlock(
        info_string=Text("swift"),
        children=[
            Text("Blah"),
        ],
    )
    assert_that(fenced_code_block.parse(tokens), expected)


def test_cloze_prompt_fails():
    tokens = lexer.parse("A throwing {cloze}\n\nprompt")
    with raises(Exception) as _:
        cloze_prompt.parse(tokens)


def test_fenced_code_block_with_prefix():
    raw = "# Title\n# Something\n```elm\nsomething\n```"
    tokens = lexer.parse(raw)
    expected = Root(
        title=Title(Text("# Title")),
        children=[
            Heading(
                prefix=HeadingPrefix(1),
                children=[
                    Text("Something"),
                ],
            ),
            Spacer(
                [
                    Break(),
                ]
            ),
            FencedCodeBlock(
                info_string=Text("elm"),
                children=[
                    Text("something"),
                ],
            ),
        ],
    )
    assert_that(parser.parse(tokens), expected)


def test_fenced_code_block_something():
    tokens = lexer.parse("```elm\nsomething\n```")
    expected = FencedCodeBlock(
        info_string=Text("elm"),
        children=[
            Text("something"),
        ],
    )
    assert_that(fenced_code_block.parse(tokens), expected)


def test_parser_code_fence():
    tokens = lexer.parse("Abc\n```\n")
    expected = Root(
        title=Title(Text("Abc")),
        children=[
            Paragraph(
                [
                    Text("```"),
                ]
            ),
            Spacer([Break()]),
        ],
    )
    assert_that(parser.parse(tokens), expected)


def test_fenced_cloze_block():
    tokens = lexer.parse("What\n```swift\nenum {\n\tdelete(Task.ID)\n}\n```")
    expected = [
        Paragraph([Text("What")]),
        Spacer([Break()]),
        FencedCodeBlock(
            info_string=Text("swift"),
            children=[
                Text("enum {"),
                Break(),
                Text("\tdelete(Task.ID)"),
                Break(),
                Text("}"),
            ],
        ),
    ]
    assert block.many().parse(tokens) == expected


def test_heading():
    tokens = lexer.parse("## Header")
    expected = Heading(
        prefix=HeadingPrefix(depth=2),
        children=[
            Text("Header"),
        ],
    )
    assert_that(heading.parse(tokens), expected)
