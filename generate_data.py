#!/usr/bin/python

import numpy as np
import cv2
import os

class GenerateData(object):
    def __init__(self, name='', shape=(480,640)):
        if len(name) <= 0:
            name = 'frame'

        self.name = name
        self.shape = shape
        self.frame = np.zeros(shape=shape)
        self.pos = []

    def start(self):

        cv2.namedWindow(self.name)
        cv2.setMouseCallback(self.name, self.track)
        cv2.imshow(self.name, self.frame)

        while True:
            cv2.imshow(self.name, self.frame)
            k = cv2.waitKey(20)
            if k == 27 or k == ord('q'):
                break

    def track(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            h,w = self.shape
            h,w = float(h), float(w)
            self.pos.append([x/w,y/h]) # normalize
            cv2.circle(self.frame, (x,y), 3, 255)

    def save(self):
        idx = 0
        for sub in os.listdir('data'):
            if sub.endswith('.npy'):
                idx += 1
        name = ('seq_%03d.npy' % idx)
        name = os.path.join('data', name)
        print ('data length : %d' % len(self.pos))
        np.save(name, np.asarray(self.pos), allow_pickle=True)

class GenerateData_v2(object):
    def __init__(self, max_seq_len=20, min_seq_len=3, noise=5e-2):

        self.max_seq_len = max_seq_len 
        self.min_seq_len = min_seq_len
        self.noise = noise

    def get(self, batch_size=1, num_steps=1, final_label=True):
        for i in range(num_steps):
            n = self.max_seq_len
            acc = np.random.randn(batch_size, 2 * n, 2) #2 = x,y
            acc -= np.mean(acc, axis=1)[:, np.newaxis, :]
            vel = np.cumsum(acc, axis=1) + np.random.randn(batch_size, 2 * n, 2)
            vel[np.abs(vel) > 5] *= 0.2


            pos = np.cumsum(vel, axis=1) + self.noise * np.random.randn(batch_size, 2 * n, 2)
            mx = np.max(np.abs(pos), axis=1)

            #pos += (mx * np.random.rand(batch_size, 2))[:, np.newaxis, :] # initial offset

            mx = np.max(np.abs(pos), axis=1)
            pos /= mx[:,np.newaxis,:]

            len = np.random.randint(self.min_seq_len, self.max_seq_len+1, size=batch_size)

            data = pos[:,n/2 : n+n/2,:] + self.noise * np.random.randn(batch_size, n, 2)

            if final_label:
                #label = np.take(pos, n/2+len, axis=1)
                label = pos[range(batch_size), n/2+len, :]
            else:
                label = pos[range(batch_size), n/2:n/2+len,range(2)]

            yield i, label, data, len

def main():
    gen = GenerateData_v2(200,100,5e-2)
    w = 640
    h = 480
    c = [w/2.,h/2.]
    frame = np.zeros((h,w), dtype=np.uint8)

    # iterate over batch
    for i, g_pos_b, d_pos_b, len_b in gen.get(batch_size=3, num_steps = 1):
        for g_pos, d_pos, len in zip(g_pos_b, d_pos_b,len_b):

            g_p = g_pos * np.array([w/2.,h/2.]) + c
            cv2.circle(frame, tuple(int(e) for e in g_p), 3, 255, thickness=-1)

            for d_p in d_pos[:len]:
                d_p = d_p * np.array([w/2.,h/2.]) + c
                cv2.circle(frame, tuple(int(e) for e in d_p), 3, 128)
                cv2.imshow('frame', frame)
                k = cv2.waitKey(20)

                if k == 27 or k == ord('q'):
                    return

            cv2.waitKey(0)

if __name__ == "__main__":
    main()

    #gen = GenerateData()
    #gen.start()
    #gen.save()