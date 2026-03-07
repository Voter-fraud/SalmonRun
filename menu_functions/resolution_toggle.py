import reso_p

def r_toggle():
    file = open('Reso.txt', 'w')
    if reso_p.res[0] == '960':
        reso_p.res = '1280', '1024'
        file.write('1280, 1024')
    elif reso_p.res[0] == '1280':
        reso_p.res = '1920', '1080'
        file.write('1920, 1080')
    else:
        reso_p.res = '960', '540'
        file.write('960, 540')
    file.close()

def r_upd():
    if reso_p.res[0] == '960':
        return 0
    elif reso_p.res[0] == '1280':
        return 1
    else: #1920
        return 2