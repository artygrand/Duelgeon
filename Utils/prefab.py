def skybox(texture):
    box = loader.loadModel('geometry/box-inverted')
    box.setTexture(loader.loadTexture(texture), 1)
    box.setScale(512)
    box.setBin('background', 1)
    box.setDepthWrite(0)
    box.setLightOff()
    box.setCompass()

    return box
