import functional
import parsy
from attrs import frozen

from .parser import EOL, Backlink, InlineText, ListItem, Note, Title, checkinstance, eol


@frozen
class Edge:
    from_node: Title
    to_node: Backlink
    children: list[InlineText | EOL | Backlink]


def build(note: Note) -> list[Edge]:
    return (
        functional.seq([note.children])
        .flat_map(split_into_paragraphs)
        .filter(lambda x: any(isinstance(ele, Backlink) for ele in x))
        .filter(lambda x: len(x) > 0)
        .flat_map(
            lambda paragraph: (
                functional.seq(paragraph)
                .filter(lambda x: isinstance(x, Backlink))
                .map(lambda backlink: Edge(note.title, backlink, paragraph))
            )
        )
        .to_list()
    )


@parsy.generate
def paragraphs():
    list_item = checkinstance(ListItem)
    result = []
    current = []

    def flush():
        nonlocal current
        if len(current) == 0:
            return
        elif current == [EOL()]:
            current = []
            return
        result.append(current)
        current = []

    while True:
        li = yield list_item.optional()
        if li is not None:
            flush()
            result.append([li])
            continue

        # TODO: Test which feels better. line or paragraphs for backlinks
        # eols = yield (eol * 2).optional()
        eols = yield eol.optional()
        if eols is not None:
            flush()
            continue

        any = yield parsy.any_char.optional()
        if any is not None:
            current.append(any)
            continue
        else:
            flush()
            result = list(filter(lambda x: len(x) > 0, result))
            return result


def split_into_paragraphs(ls):
    return paragraphs.parse(ls)
