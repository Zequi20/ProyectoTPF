function Header(el)
  if el.level == 1 and pandoc.utils.stringify(el):match("^Referencias") then
    return {el, pandoc.Div({}, pandoc.Attr("refs"))}
  end
end
