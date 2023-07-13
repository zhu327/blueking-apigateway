// Code generated by MockGen. DO NOT EDIT.
// Source: release.go

// Package mock is a generated GoMock package.
package mock

import (
	context "context"
	reflect "reflect"

	dao "core/pkg/database/dao"

	gomock "github.com/golang/mock/gomock"
)

// MockReleaseManager is a mock of ReleaseManager interface.
type MockReleaseManager struct {
	ctrl     *gomock.Controller
	recorder *MockReleaseManagerMockRecorder
}

// MockReleaseManagerMockRecorder is the mock recorder for MockReleaseManager.
type MockReleaseManagerMockRecorder struct {
	mock *MockReleaseManager
}

// NewMockReleaseManager creates a new mock instance.
func NewMockReleaseManager(ctrl *gomock.Controller) *MockReleaseManager {
	mock := &MockReleaseManager{ctrl: ctrl}
	mock.recorder = &MockReleaseManagerMockRecorder{mock}
	return mock
}

// EXPECT returns an object that allows the caller to indicate expected use.
func (m *MockReleaseManager) EXPECT() *MockReleaseManagerMockRecorder {
	return m.recorder
}

// Get mocks base method.
func (m *MockReleaseManager) Get(ctx context.Context, gatewayID, stageID int64) (dao.Release, error) {
	m.ctrl.T.Helper()
	ret := m.ctrl.Call(m, "Get", ctx, gatewayID, stageID)
	ret0, _ := ret[0].(dao.Release)
	ret1, _ := ret[1].(error)
	return ret0, ret1
}

// Get indicates an expected call of Get.
func (mr *MockReleaseManagerMockRecorder) Get(ctx, gatewayID, stageID interface{}) *gomock.Call {
	mr.mock.ctrl.T.Helper()
	return mr.mock.ctrl.RecordCallWithMethodType(mr.mock, "Get", reflect.TypeOf((*MockReleaseManager)(nil).Get), ctx, gatewayID, stageID)
}
