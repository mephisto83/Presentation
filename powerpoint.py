import json
from pptx import Presentation
from pptx.shapes.placeholder import SlidePlaceholder
from pptx.shapes.autoshape import Shape
from pptx.text.text import Font
from pptx.util import Length, Centipoints, Cm, Emu, Inches, Mm, Pt, Px
import pptx
import inspect
prs = Presentation('existing.pptx')
slide = prs.slides[0]
print("shape count : {}".format(len(slide.shapes)))
output_slides = []
def iter_rPrs(txBody):
    for p in txBody.p_lst:
        for elm in p.content_children:
            yield elm.get_or_add_rPr()
        # generate a:endParaRPr for each <a:p> element
        yield p.get_or_add_endParaRPr()
for shape in slide.shapes:
    panel = {}
    output_slides.append(panel)
    fff = Font(shape.text_frame._element.p_lst[0].content_children[0].get_or_add_rPr())
    print(fff)
    print("name {} ".format(fff.name))
    panel["font"] = fff.name
    if fff.size != None:
        print("size {} ".format(Length(fff.size).pt))
        panel["size"] = Length(fff.size).pt
    print("fill {} ".format(fff.fill))
    for txBody in shape._element:
        try:
            if hasattr(txBody, "p_lst"):
                print("txBody")
                print(txBody)
                for rPr in iter_rPrs(txBody):
                    print("font")
                    fon = Font(rPr)
                    
            
        except:
            print("error")
            continue
    panel["marginBottom"] = Length(shape.text_frame.margin_bottom).pt
    panel["marginTop"] = Length(shape.text_frame.margin_top).pt
    panel["marginLeft"] = Length(shape.text_frame.margin_left).pt
    panel["marginRight"] = Length(shape.text_frame.margin_right).pt
    if hasattr(shape, "text"):
        print("text {}".format(shape.text))
        panel["text"] = shape.text
    if hasattr(shape, "height"):
        print("height {}".format(Length(shape.height).pt))
        panel["height"] = Length(shape.height).pt
    if hasattr(shape, "width"):
        print("width {}".format(Length(shape.width).pt))
        panel["width"] = Length(shape.width).pt
    if hasattr(shape, "left"):
        print("left {}".format(Length(shape.left).pt))
        panel["left"] = Length(shape.left).pt
    if hasattr(shape, "top"):
        print("top {}".format(Length(shape.top).pt))
        panel["top"] = Length(shape.top).pt
    if hasattr(shape, "rotation"):
        print("rotation {}".format(shape.rotation))
        panel["rotation"] = shape.rotation
    if hasattr(shape, "name"):
        print("name {}".format(shape.name))
        panel["name"] = shape.name

print(output_slides)
print(json.dumps(output_slides, sort_keys=True, indent=4, separators=(',', ': ')))
# prs.save('test.pptx')
