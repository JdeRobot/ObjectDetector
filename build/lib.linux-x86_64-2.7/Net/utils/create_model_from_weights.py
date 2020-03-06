import h5py
from keras.optimizers import Adam

from Net.Keras.models.keras_ssd300 import ssd_300
from Net.Keras.models.keras_ssd512 import ssd_512


def create_model(file, ssd_loss, n_classes):

    h5_file = h5py.File(file, 'r')

    size = h5_file.items()[0][1].items()[0][1].items()[0][1].shape[0]
    if size == 64:
      model = ssd_300(image_size=(300, 300, 3),
         n_classes = n_classes,
         mode='inference',
         l2_regularization=0.0005,
        scales=[0.1, 0.2, 0.37, 0.54, 0.71, 0.88, 1.05], # The scales for MS COCO are [0.07, 0.15, 0.33, 0.51, 0.69, 0.87, 1.05]
            aspect_ratios_per_layer=[[1.0, 2.0, 0.5],
            [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
            [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
            [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
            [1.0, 2.0, 0.5],
            [1.0, 2.0, 0.5]],
            two_boxes_for_ar1=True,
            steps=[8, 16, 32, 64, 100, 300],
            offsets=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            clip_boxes=False,
            variances=[0.1, 0.1, 0.2, 0.2],
            coords='centroids',
            normalize_coords=True,
            subtract_mean=[123, 117, 104],
            swap_channels=[2, 1, 0],
            confidence_thresh=0.5,
            iou_threshold=0.45,
            top_k=200,
            nms_max_output_size=400)

    elif size == 128:
        print("512x512")

        model = ssd_512(image_size=(512, 512, 3),
                        n_classes=n_classes,
                        mode='inference',
                        l2_regularization=0.0005,
                        scales=[0.07, 0.15, 0.3, 0.45, 0.6, 0.75, 0.9, 1.05], # The scales for MS COCO are [0.04, 0.1, 0.26, 0.42, 0.58, 0.74, 0.9, 1.06]
                        aspect_ratios_per_layer=[[1.0, 2.0, 0.5],
                        [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
                        [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
                        [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
                        [1.0, 2.0, 0.5, 3.0, 1.0/3.0],
                        [1.0, 2.0, 0.5],
                        [1.0, 2.0, 0.5]],
                        two_boxes_for_ar1=True,
                        steps=[8, 16, 32, 64, 128, 256, 512],
                        offsets=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
                        clip_boxes=False,
                        variances=[0.1, 0.1, 0.2, 0.2],
                        coords='centroids',
                        normalize_coords=True,
                        subtract_mean=[123, 117, 104],
                        swap_channels=[2, 1, 0],
                        confidence_thresh=0.5,
                        iou_threshold=0.45,
                        top_k=200,
                        nms_max_output_size=400)

    else:
      SystemExit('Error: unknown network size')

    model.load_weights(file, by_name=True)

    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=5e-04)

    model.compile(optimizer=adam, loss=ssd_loss.compute_loss)

    # Save the full model on a complete HDF5 file.

    full_model_name = file.split('.h5')[0] + '_full' + '.h5'
    model.save(full_model_name)


    return model