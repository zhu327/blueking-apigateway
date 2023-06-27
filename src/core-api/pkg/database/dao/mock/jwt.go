// Code generated by MockGen. DO NOT EDIT.
// Source: jwt.go

// Package mock is a generated GoMock package.
package mock

import (
	context "context"
	dao "core/pkg/database/dao"
	reflect "reflect"

	gomock "github.com/golang/mock/gomock"
)

// MockJWTManager is a mock of JWTManager interface.
type MockJWTManager struct {
	ctrl     *gomock.Controller
	recorder *MockJWTManagerMockRecorder
}

// MockJWTManagerMockRecorder is the mock recorder for MockJWTManager.
type MockJWTManagerMockRecorder struct {
	mock *MockJWTManager
}

// NewMockJWTManager creates a new mock instance.
func NewMockJWTManager(ctrl *gomock.Controller) *MockJWTManager {
	mock := &MockJWTManager{ctrl: ctrl}
	mock.recorder = &MockJWTManagerMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockJWTManager) EXPECT() *MockJWTManagerMockRecorder {
	return m.recorder
}

// Get mocks base method.
func (m *MockJWTManager) Get(ctx context.Context, gatewayID int64) (dao.JWT, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Get", ctx, gatewayID)
	ret0, _ := ret[0].(dao.JWT)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// Get indicates an expected call of Get.
func (mr *MockJWTManagerMockRecorder) Get(ctx, gatewayID interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Get", reflect.TypeOf((*MockJWTManager)(nil).Get), ctx, gatewayID)
}
