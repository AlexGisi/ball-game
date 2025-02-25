import numpy as np
from scipy.linalg import expm
from math import floor

import util
from constants import *


class pid:
    def __init__(self, kp, kd, ki):
        self.kp = kp
        self.kd = kd
        self.ki = ki
        
        self.e_last = 0
        self.e_cum = 0
        
    def control(self, y_ref, y_ball):
        error = y_ref - y_ball
        print(error)

        de = error - self.e_last
        self.e_last = error
        self.e_cum += error
        
        return error * self.kp + de * self.kd + self.ki * self.e_cum
    
    def reset(self):
        pass
    

class OperatorModel:
    def __init__(self, ball_state) -> None:
        self.delay = 0.15  # Effective (perception) time delay

        Q = np.array([
            [0.0, 0.0],
            [0.0, 0.0]
        ])  # Process noise covariance
        R = np.array([[0.1]])  # Observation noise covariance
        
        self.F = ball_state.A
        self.B = ball_state.B
        self.H = ball_state.C
        self.kalman = Kalman(ball_state.Ad,  # Discretized A matrix
                             ball_state.Bd,  # Discretized b vector
                             ball_state.C,
                             Q, R)
        self.predictor = Predictor(ball_state.A, ball_state.B, self.delay)
        
        # self.control_gains = np.array([1.0, 1.0])
        self.pid = pid(0.01, 0.0, 0.0)
        
        self.state = np.zeros_like(self.B)
        self.delayed_perceptions = [0 for _ in range(floor(self.delay*FPS))]

    def control(self, y_ref, y_ball):
        observation_noise = np.random.normal(0, 0.01 * y_ball**2)  # Pi=0.01, see McRuer 1980 p248
        observation = y_ball + observation_noise

        # Time delay
        self.delayed_perceptions.append(observation)
        perception = self.delayed_perceptions.pop(0)

        # Internal model of man/machine system
        xhat_kalman, _ = self.kalman.step(perception)  # Delayed state estimation
        xhat = self.predictor.step(xhat_kalman)  # Current state estimation

        # print(f"actual: {y_ball}:.2f, perception: {perception}, kalman: {xhat_kalman}, xhat: {xhat}")

        # Controller
        # u = self.control_gains @ xhat
        yhat = float((self.H @ xhat)[0, 0])
        uhat = self.pid.control(y_ref, yhat)

        # Motor system commmands
        motor_noise = np.random.normal(0, 0.003 * uhat**2)  # Pmi=0.003
        u = uhat + motor_noise

        # print(f"yhat: {yhat}, uhat: {uhat}, u: {u}")

        return u


    def reset(self):
        self.state = np.zeros_like(self.B)


class Kalman:
    def __init__(self, F, B, H, Q, R):
        self.F = F
        self.B = B
        self.H = H
        self.Q = Q
        self.R = R

        self.xhat = np.zeros((F.shape[0], 1))
        self.P = np.array([
            [1.0, 0.0],
            [0.0, 1.0],
        ]) * 10**-4

    def step(self, z):
        # Predict
        xpred = self.F @ self.xhat
        Ppred = self.F @ self.P @ self.F.T + self.Q
        
        # Update
        yk = z - self.H @ xpred  # Innovation
        Sk = self.H @ Ppred @ self.H.T + self.R  # Innovation covariance
        Kk = Ppred @ self.H.T @ np.linalg.inv(Sk)  # Kalman gain

        self.xhat = xpred + Kk @ yk
        self.P = (np.eye(self.xhat.shape[0]) - Kk @ self.H) @ Ppred

        return self.xhat, self.P
    

class Predictor:
    """See page 827, "A Control-Theoretic Approach to Manned-Vehicle 
    Systems Analysis", Kleinman et al.
    """
    def __init__(self, A, B, tau):
        # self.A1 = np.block([[A, b], [np.zeros_like((1, A.shape[1])), -1/tau_n]])
        # self.b0 = np.zeros((self.A1.shape[0], 1))
        # self.b0[-1, 0] = 1.0

        # self.zeta = np.zeros_like((self.A1.shape[0], 1))
        # self.past_zetas = [np.zeros_like((self.A1.shape[0], 1)) for _ in range(np.floor(tau*FPS))]

        self.A = A
        self.B = B
        self.tau = tau

        self.zeta = np.zeros((self.A.shape[0], 1))
        self.past_zetas = [np.zeros((self.A.shape[0], 1)) for _ in range(floor(tau*FPS))]


    def step(self, kalman_prediction):
        # Predict
        Ad, _ = util.discretized_lti(self.A, self.B)
        self.zeta = Ad @ self.zeta

        self.past_zetas.append(self.zeta)
        delayed_zeta = self.past_zetas.pop(0)

        # Update
        xhat = self.zeta + expm(self.A * self.tau) @ (kalman_prediction - delayed_zeta)
        
        return xhat


if __name__ == '__main__':
    def test_hom():
        hom = OperatorModel()
        # p = pid(0.1, 0.0, 0.1)

        ts = np.arange(0, 10, 0.01)
        xs = np.where(ts > 1.0, 1.0, 0.0)
        ys = np.zeros_like(xs)
        e = xs[0] - ys[0]
        for i, x in enumerate(xs):
            ys[i] = hom.control(e)
            e = x - ys[i]
            print(e)

        import matplotlib.pyplot as plt
        plt.plot(ts, ys, label='output')
        plt.plot(ts, xs, label='input')
        plt.legend()
        plt.show()

    def test_kalman():
        import matplotlib.pyplot as plt

        # Define system parameters
        dt = 0.1
        F = np.array([[1, dt],
                    [0, 1]])
        B = np.zeros((2,1))  # no control input
        H = np.array([[1, 0]])
        Q = np.array([[1e-3, 0],
                    [0, 1e-3]])
        R = np.array([[1e-1]])  # measurement noise covariance

        # True initial state
        x_true = np.array([[0.0],
                        [1.0]])  # position=0, velocity=1 m/s

        # Generate synthetic data
        N = 100
        true_states = []
        measurements = []
        time = np.arange(N)*dt

        for k in range(N):
            # Save true state
            true_states.append(x_true.copy())

            # Generate measurement (just position + noise)
            z = H @ x_true + np.sqrt(R)*np.random.randn(1,1)
            measurements.append(z)

            # Propagate true state (without process noise for simplicity)
            x_true = F @ x_true  # deterministic model

        true_states = np.hstack(true_states)
        measurements = np.hstack(measurements)

        # Instantiate Kalman filter
        kf = Kalman(F=F, B=B, H=H, Q=Q, R=R)

        estimates = []
        for k in range(N):
            z = measurements[:, k].reshape(-1,1)
            xhat, P = kf.step(z)
            estimates.append(xhat)

        estimates = np.hstack(estimates)

        # Plot results
        plt.figure(figsize=(10,6))
        plt.subplot(2,1,1)
        plt.plot(time, true_states[0,:], 'k-', label='True Position')
        plt.plot(time, measurements[0,:], 'rx', label='Measurements')
        plt.plot(time, estimates[0,:], 'b-', label='Estimated Position')
        plt.legend(loc='best')
        plt.title('Position')

        plt.subplot(2,1,2)
        plt.plot(time, true_states[1,:], 'k-', label='True Velocity')
        plt.plot(time, estimates[1,:], 'b-', label='Estimated Velocity')
        plt.legend(loc='best')
        plt.title('Velocity')

        plt.xlabel('Time (s)')
        plt.tight_layout()
        plt.show()
    
    test_kalman()
    # test_hom()
    