import dtk, logging

level = logging.ERROR

e = dtk.Engine(name='dtk Test App')
e.beginLogging(file = 'log.txt', level = level)

cols = dtk.Columns()


rows = dtk.Rows()
lb = dtk.ListBox()

lll = []
for i in "eins zwei drei vier fuenf".split():
    lll.append(i)

text = dtk.TextEditor()
text.setText("This is the text")

lb.setItems(lll)

rows.addRow(lb)
rows.addRow(text)

def dothings():
    rows.log.error("switching child")
    rows.nextRow()

rows.bindKey('tab', dothings)

text.bindEvent("lost focus", text.log.error, "lost focus")
text.bindEvent("got focus", text.log.error, "got focus")



cols.addColumn(rows)
cols.addColumn(dtk.Label(text='Hi'))
cols.bindKey('F1', cols.nextColumn)

e.setRoot(cols)

e.bindKey('q', e.quit)

e.mainLoop()
