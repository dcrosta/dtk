import dtk
import logging

e = dtk.Engine()
e.beginLogging(file='log.txt', level=logging.DEBUG)

c = dtk.Columns()
l = dtk.ListBox()
l.setItems([
        'Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Nullam ac elit. Nullam consectetuer ultrices elit. Morbi a sem.',
        'Sed urna. Nam magna erat, pellentesque quis, ultricies id, hendrerit molestie, nibh. Cras placerat pellentesque erat.',
        'Vestibulum fringilla, ligula eget tristique convallis, enim risus dignissim lacus, at pharetra velit purus vitae lectus.',
        'Vivamus aliquet vehicula nunc. Nulla commodo ligula eu felis. Duis eu sapien quis leo posuere rutrum. Suspendisse porttitor',
        'pulvinar elit. In scelerisque elit a elit. Praesent accumsan. Fusce sed lacus in lectus varius aliquam. Proin lobortis.',
        'Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Suspendisse aliquam ultrices pede.',
        'Suspendisse bibendum dolor vel diam. Morbi vel arcu vitae magna fermentum interdum. Donec ornare sollicitudin enim.'
        ])

c.addColumn(l)
c.bindKey('q', e.quit)

e.setRoot(c)

e.mainLoop()

