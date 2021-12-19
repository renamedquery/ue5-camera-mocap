import urllib.request, requests, time

PHONEPI_SERVER_ADDR_ORIENTATION = 'http://127.0.0.1:5000/orientation_read'
PHONEPI_SERVER_ADDR_ACCEL = 'http://127.0.0.1:5000/accelerometer_read'
UE5_REMOTE_CONTROL_SERVER_ADDR = 'http://127.0.0.1:6001/remote/object/call'

BEGINNER_ARRAY = [
    0,0,0,0,0,0,0,0,0,0,0,0
]

rotationMultiplier = 1
accelerationMultiplier = 1

# gyro
requestBody = {
    "objectPath" : "/Game/MainMap.MainMap:PersistentLevel.DefaultPawn_C_1",
    "functionName" : "SetActorRotation",
    "parameters" : {
        "NewRotation" : {
            "Pitch" : 0,
            "Yaw" : 0,
            "Roll" : 0,
        }
    },
    "generateTransaction" : False
}

# accel
requestBody_accel = {
    "objectPath" : "/Game/MainMap.MainMap:PersistentLevel.DefaultPawn_C_1",
    "functionName" : "SetActorRelativeLocation",
    "parameters" : {
        "X" : 0,
        "Y" : 0,
        "Z" : 0,
    },
    "generateTransaction" : False
}

# gyro
lastFewPointsX = BEGINNER_ARRAY
lastFewPointsY = BEGINNER_ARRAY
lastFewPointsZ = BEGINNER_ARRAY

cumulativeRotation = [0, 0, 0]

# accel
lastFewPointsX_accel = BEGINNER_ARRAY
lastFewPointsY_accel = BEGINNER_ARRAY
lastFewPointsZ_accel = BEGINNER_ARRAY

cumulativeAcceleration = [0, 0, 0]

def avg(arr) -> float:

    return sum(arr) / len(arr)

while (1):

    try:

        print(time.time())

        dataFromPhonePi = urllib.request.urlopen(PHONEPI_SERVER_ADDR_ORIENTATION).read().decode().split(',')
        dataFromPhonePi_accel = [0, 0, 0] #urllib.request.urlopen(PHONEPI_SERVER_ADDR_ACCEL).read().decode().split(',')

        x, y, z = float(dataFromPhonePi[-3]), float(dataFromPhonePi[-2]), float(dataFromPhonePi[-1])
        x_accel, y_accel, z_accel = float(dataFromPhonePi[-3]) * accelerationMultiplier, float(dataFromPhonePi[-2]) * accelerationMultiplier, float(dataFromPhonePi[-1]) * accelerationMultiplier

        rotationDelta = [x - lastFewPointsX[-1], y - lastFewPointsY[-1], z - lastFewPointsZ[-1]]
        accelerationDelta = [x_accel - lastFewPointsX_accel[-1], y_accel - lastFewPointsY_accel[-1], z_accel - lastFewPointsZ_accel[-1]]

        for i in range(3):

            if (rotationDelta[i] > 360 // 2):

                rotationDelta[i] -= 360
            
            elif (rotationDelta[i] < -360 // 2):

                rotationDelta[i] += 360

        cumulativeRotation[0] += rotationDelta[0]
        cumulativeRotation[1] += rotationDelta[1]
        cumulativeRotation[2] += rotationDelta[2]

        lastFewPointsX = [*lastFewPointsX[1:], cumulativeRotation[0]]
        lastFewPointsY = [*lastFewPointsY[1:], cumulativeRotation[1]]
        lastFewPointsZ = [*lastFewPointsZ[1:], cumulativeRotation[2]]

        lastFewPointsX_accel = [*lastFewPointsX_accel[1:], x_accel]
        lastFewPointsY_accel = [*lastFewPointsY_accel[1:], y_accel]
        lastFewPointsZ_accel = [*lastFewPointsZ_accel[1:], z_accel]

        x, y, z = avg(lastFewPointsX), avg(lastFewPointsY), avg(lastFewPointsZ) 
        x_accel, y_accel, z_accel = avg(lastFewPointsX_accel), avg(lastFewPointsY_accel), avg(lastFewPointsZ_accel) # average - dont know if this will be needed

        cumulativeAcceleration[0] += accelerationDelta[0]
        cumulativeAcceleration[1] += accelerationDelta[1]
        cumulativeAcceleration[2] += accelerationDelta[2]

        requestBody['parameters']['NewRotation']['Yaw'] = -x * rotationMultiplier
        requestBody['parameters']['NewRotation']['Pitch'] = -z * rotationMultiplier
        requestBody['parameters']['NewRotation']['Roll'] = 0 #z * rotationMultiplier

        requests.put(UE5_REMOTE_CONTROL_SERVER_ADDR, json = requestBody)

        requestBody_accel['parameters']['X'] = cumulativeAcceleration[0]
        requestBody_accel['parameters']['Y'] = cumulativeAcceleration[1]
        requestBody_accel['parameters']['Z'] = cumulativeAcceleration[2]

        #requests.put(UE5_REMOTE_CONTROL_SERVER_ADDR, json = requestBody_accel)

        print(cumulativeAcceleration)
        print(cumulativeRotation)

    except KeyboardInterrupt:

        exit()